"""
This module is to define the GraphQL queries and mutations
of the `notifier` app.
"""

import dataclasses
import hashlib
import hmac
import json
from typing import List, Optional, cast

import strawberry
import strawberry.django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django_q.models import Schedule
from django_q.tasks import async_task, logger
from graphql.error import GraphQLError
from strawberry.scalars import JSON
from strawberry.types import Info
from strawberry_django.fields.types import OperationMessage
from strawberry_django.permissions import IsAuthenticated

from data import SubjectEnum
from telegram_bot.models import TelegramProfile
from telegram_bot.utils import escape_md

from .models import Banner, ChannelEnum, Course, RegisterCourse, TrackingList
from .types import (
    ChannelsType,
    CourseInput,
    PreferencesInput,
    RegisterCourseInput,
    RegisterCourseType,
    TermType,
)
from .utils import fetch_data, get_course_info, instructor_info_from_name

User = get_user_model()


def resolve_subject_list(root, info: Info, short: bool = True) -> List[str]:
    subject_short: List[str] = []
    subject_long: List[str] = []
    for short_, long_ in SubjectEnum.choices:
        subject_short.append(short_)
        subject_long.append(long_)

    if short:
        return subject_short

    return subject_long


@strawberry.type
class Query:
    """Main entry of all Query types of `notifier` app."""

    terms: List[TermType] = strawberry.django.field()

    @strawberry.field(extensions=[IsAuthenticated()])
    def register_course_by_crn(self, info: Info, crn: str) -> RegisterCourseType:
        """Returns `RegisterCourse` obj for current logged in user."""

        user = info.context.request.user
        assert isinstance(user, User), "ERROR_CODE: skill issue."

        tl = TrackingList.objects.get(user=user)

        return cast(RegisterCourseType, tl.registercourse_set.get(course__crn=crn))

    @strawberry.field
    def raw_data(self, term: int, department: str) -> JSON:
        """
        The raw data directly from the API.
        """

        return fetch_data(term, department)

    @strawberry.field(extensions=[IsAuthenticated()])
    def tracking_list_channels(self, info: Info) -> Optional[ChannelsType]:
        """Get the user's tracking list tracking_list_channels."""

        user = info.context.request.user

        res = {}
        for name in ChannelEnum.names:
            res |= {name: ChannelEnum[name] in user.tracking_list.channels}

        return ChannelsType(**res)

    subject_list = strawberry.field(resolve_subject_list)

    @strawberry.field(extensions=[IsAuthenticated()])
    def tracked_courses(self, info: Info) -> Optional[JSON]:
        """
        get all tracked courses' CRNs by the
        current logged in user.

        Returns:
            List[CourseType]: List of courses CRNs
            return False if no `TrackingList` found
            for the user.
        """

        user = info.context.request.user
        try:
            tracking_list = TrackingList.objects.get(user=user)
        except TrackingList.DoesNotExist:
            return False

        result = []

        for course in tracking_list.registercourse_set.all():
            # frontend needs courses to be in Banner format, not just `Course` obj
            for raw_course in fetch_data(course.course.term, course.course.department):
                if course.course.crn == raw_course["courseReferenceNumber"]:
                    result.append(raw_course)

        return result

    @strawberry.field
    def search(self, term: str, department: str, title: str) -> JSON:
        """to call `fetch_data`
        and perform case-insensitive searching
        in the `course_number` and `course_title` fields from API data.

        Args:
            term (int): term number
            department (str): in which department
            title (str): case-insensitive title of the course or code

        Returns:
            JSON: the same structure of the API data.
        """

        # TODO: We shouldn't keep calling db for this better cache it.
        raw = fetch_data(term, department)

        result = []
        for course in raw:
            if title.lower() in course["subjectCourse"].lower():
                result.append(course)

                # try to find some info about this instructor
                # and append it to the course dict
                for faculty in course["faculty"]:
                    if len(faculty["displayName"]) > 1:
                        faculty |= instructor_info_from_name(
                            faculty["displayName"], department
                        )

        return result


@strawberry.type
class Mutation:
    """Main entry of all Mutation types of `notifier` app."""

    @strawberry.mutation(extensions=[IsAuthenticated()])
    def save_banner_session(self, info: Info, cookies: str) -> bool:
        user = info.context.request.user
        try:
            obj, _ = Banner.objects.get_or_create(user=user)
            if obj.scheduler:
                obj.scheduler.delete()

            # create a schedule for 10 min forever, starting now
            s = Schedule(
                name="check_session",
                func="notifier.utils.check_session",
                schedule_type=Schedule.MINUTES,
                args=(user.pk,),
                minutes=10,
                kwargs=None,
                hook=None,
                cron=None,
            )
            # make sure we trigger validation
            s.full_clean()
            s.save()

            obj.cookies = json.loads(cookies)
            obj.scheduler = s
            obj.save()

        except Exception as e:
            logger.error("Error in saving Banner for user %s: %s", user.pk, e)
            return False

        return True

    @strawberry.mutation(extensions=[IsAuthenticated()])
    def register_course_update(
        self, info: Info, data: RegisterCourseInput
    ) -> OperationMessage:
        """
        Updates user's `RegisterCourse` fields, given by courses' CRN.

        Args:
            info (Info): given by GraphQL
            courses (List[CourseInput]): A list of CourseInput

        Returns:
            bool: A success flag
        """

        user = info.context.request.user
        assert isinstance(user, User), "ERROR_CODE: skill issue."

        try:
            tl = user.tracking_list
            rc = tl.registercourse_set.get(pk=data.id)
            rc.strategy = data.strategy

            if data.strategy == RegisterCourse.RegisterStrategyEnum.LINKED_LAB:
                rc.with_add = Course.objects.get(crn=data.with_add_crn)

            elif data.strategy == RegisterCourse.RegisterStrategyEnum.REPLACE_WITH:
                rc.with_add = Course.objects.get(crn=data.with_drop_crn)

            rc.save()

        except ObjectDoesNotExist:
            return OperationMessage(
                kind=OperationMessage.Kind.VALIDATION, message="CRN not found."
            )

        except Exception as e:
            logger.error(
                "Couldn't update `RegisterCourse` with %s for user %s: %s",
                data,
                user.pk,
                e,
            )
            return OperationMessage(
                kind=OperationMessage.Kind.ERROR,
                message="We have no idea what just happened :(",
            )

        return OperationMessage(
            kind=OperationMessage.Kind.INFO, message="Updated.", code="SUCCESS"
        )

    @strawberry.mutation(extensions=[IsAuthenticated()])
    def toggle_register_course(self, info: Info, crn: str) -> bool:
        """
        This takes the CRN of a course to add/remove it to/from
        user's TrackingList.
        """
        # FIXME: This should handle updateing course register strategy

        raise NotImplemented("This feature needs a new implementation.")

        user = info.context.request.user
        try:
            course = Course.objects.get(crn=crn)

            if user.tracking_list.register_courses.filter(crn=crn):
                user.tracking_list.register_courses.remove(course)
            else:
                user.tracking_list.register_courses.add(course)

            return True

        except Exception as e:
            logger.error(
                "Couldn't toggle register course %s for user %s: %s", crn, user.pk, e
            )
            return False

    @strawberry.mutation(extensions=[IsAuthenticated()])
    def update_tracking_list_channels(self, info: Info, data: PreferencesInput) -> bool:
        """To update user's tracking list preferences.
        This also is responsible for creating TrackingList for
        first time user and `TelegramProfile`"""

        # we don't support notifications on email
        if data.channels.EMAIL:
            raise ValueError(
                "We don't support sending notification through email anymore."
            )

        user = info.context.request.user
        tracking_list, cerated = TrackingList.objects.get_or_create(user=user)
        channels = dataclasses.asdict(data.channels)

        # loop through provided channels, add them to the user's tracking list
        tracking_list.channels = set()
        for channel, checked in channels.items():
            if checked and channel != ChannelEnum.TELEGRAM.name:
                tracking_list.channels.add(ChannelEnum[channel])

        # ! check for the hashing and return false to the caller if the hashing was incorrect
        if data.channels.TELEGRAM:
            if data.telegram_id and data.dataCheckString:
                # calculate the hash from check string
                message = (
                    data.dataCheckString.encode("utf-8")
                    .decode("unicode-escape")
                    .encode("ISO-8859-1")
                )
                check_hash = hmac.new(
                    key=hashlib.sha256(
                        bytes(settings.TELEGRAM_TOKEN, "utf-8")
                    ).digest(),
                    msg=message,
                    digestmod=hashlib.sha256,
                ).hexdigest()

                if check_hash == data.hash:
                    # if the hash match
                    # try to get or create a `TelegramProfile` obj
                    try:
                        telegram_profile = TelegramProfile.objects.get(
                            id=int(data.telegram_id)
                        )
                        # setting the user again, it might be a new account
                        telegram_profile.user = user
                        telegram_profile.save()

                    except TelegramProfile.DoesNotExist:
                        TelegramProfile.objects.create(
                            id=int(data.telegram_id),
                            user=user,
                        )

                    tracking_list.channels.add(ChannelEnum.TELEGRAM)

                    async_task(
                        "telegram_bot.utils.send_telegram_message",
                        task_name=f"sending-success-connection-{user.pk}",
                        group="telegram_connection",
                        chat_id=int(data.telegram_id),
                        msg=f"Hey {escape_md(user.username)}, "
                        "we connected your telegram with Petroly \\!",
                    )
            else:
                if cerated:
                    # if `TrackingList` is just created remove
                    tracking_list.delete()

                logger.warning(
                    "Issue in setting Telegram ID for user %s: %s %s",
                    user.pk,
                    data.telegram_id,
                    data.dataCheckString,
                )
                return False

        tracking_list.save()
        logger.warning(
            "Request to update channels but nothing changed for user %s: %s",
            user.pk,
            data,
        )

        return True

    @strawberry.mutation(extensions=[IsAuthenticated()])
    def update_tracking_list(self, info: Info, courses: List[CourseInput]) -> bool:
        """Add all `courses` to the user's tracking list
        then update each course status from the cache.

        Args:
            info (Info): given by GraphQL
            courses (List[CourseInput]): A list of CourseInput

        Returns:
            bool: A success flag
        """
        user = info.context.request.user
        tracking_list, _ = TrackingList.objects.get_or_create(user=user)

        if user.profile.premium:
            if len(courses) > 30:
                raise GraphQLError("Sorry you can't track more than 30 sections.")
        else:
            if len(courses) > 15:
                raise GraphQLError("Sorry you can't track more than 15 sections.")

        try:
            new_rc_pks = []
            for course in courses:
                obj, _ = Course.objects.get_or_create(
                    crn=course.crn,
                    term=course.term,
                    department=course.department,
                )
                rc, created = RegisterCourse.objects.get_or_create(
                    course=obj, tracking_list=tracking_list
                )
                if created:
                    rc.make_strategy_off()  # NOTE: Redundent

                new_rc_pks.append(rc.pk)

                # always update the status from our cache
                # This will guarantee that the course status is to date
                # before it's being tracked avoiding false notification
                course_info = get_course_info(cast(Course, course))
                obj.available_seats = course_info["seatsAvailable"]
                obj.waiting_list_count = course_info["waitAvailable"]
                obj.raw = course_info
                obj.save()

            # DB-delete any `RegisterCourse` obj not in `new_rc_pks`, that's
            # how we untrack courses for a user with the new implementaion.
            RegisterCourse.objects.filter(tracking_list=tracking_list).exclude(
                pk__in=new_rc_pks
            ).delete()

        except Exception as exc:
            print(
                f"Error while updating the tracking list for user {user.pk}: ",
                exc,
            )
            return False

        return True
