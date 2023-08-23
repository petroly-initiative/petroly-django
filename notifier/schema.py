"""
This module is to define the GraphQL queries and mutations
of the `notifier` app.
"""

import hmac
import hashlib
import dataclasses
from typing import List, Optional

import strawberry
from strawberry.scalars import JSON
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import IsAuthenticated
from django.conf import settings
from django_q.tasks import async_task, logger

from telegram_bot.models import TelegramProfile
from telegram_bot.utils import escape_md

from data import SubjectEnum
from .utils import fetch_data, get_course_info, instructor_info_from_name
from .models import Term, TrackingList, Course, ChannelEnum
from .types import CourseInput, TermType, ChannelsType, PreferencesInput


def resolve_subject_list(root, info: Info, short: bool = True) -> List[str]:
    subject_short: List[str] = []
    subject_long: List[str] = []
    for short_, long_ in SubjectEnum.choices:
        subject_short.append(short_)
        subject_long.append(long_)

    if short:
        return subject_short

    return subject_long


@gql.type
class Query:
    """Main entry of all Query types of `notifier` app."""

    terms: List[TermType] = gql.django.field()

    @gql.field
    def raw_data(self, term: int, department: str) -> JSON:
        """
        The raw data directly from the API.
        """

        return fetch_data(term, department)

    @gql.field(directives=[IsAuthenticated()])
    def tracking_list_channels(self, info: Info) -> Optional[ChannelsType]:
        """Get the user's tracking list tracking_list_channels."""

        user = info.context.request.user

        res = {}
        for name in ChannelEnum.names:
            res |= {name: ChannelEnum[name] in user.tracking_list.channels}

        return ChannelsType(**res)

    subject_list = strawberry.field(resolve_subject_list)

    @gql.field(directives=[IsAuthenticated()])
    def tracked_courses(self, info: Info) -> Optional[JSON]:
        """get all tracked courses' CRNs by the
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
        for course in tracking_list.courses.all():
            for raw_course in fetch_data(course.term, course.department):
                if course.crn == raw_course["courseReferenceNumber"]:
                    result.append(raw_course)

        return result

    @gql.field
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

        # TODO We shouldn't keep calling db for this
        # better cache it.
        if not term or term not in Term.objects.values_list("long", flat=True):
            raise Exception("You should specify a valid term.")

        if not department or department not in SubjectEnum.values:
            raise Exception("You should specify a valid department.")

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


@gql.type
class Mutation:
    """Main entry of all Mutation types of `notifier` app."""

    @gql.mutation(directives=[IsAuthenticated()])
    def update_tracking_list_channels(
        self, info: Info, input: PreferencesInput
    ) -> bool:
        """To update user's tracking list preferences.
        This also is responsible for creating TrackingList for
        first time user and `TelegramProfile`"""

        # we don't support notifications on email
        if input.channels.EMAIL:
            raise ValueError(
                "We don't support sending notification through email anymore."
            )

        user = info.context.request.user
        tracking_list, cerated = TrackingList.objects.get_or_create(user=user)
        channels = dataclasses.asdict(input.channels)

        # loop through provided channels, add them to the user's tracking list
        tracking_list.channels = set()
        for channel, checked in channels.items():
            if checked and channel != ChannelEnum.TELEGRAM.name:
                tracking_list.channels.add(ChannelEnum[channel])

        # ! check for the hashing and return false to the caller if the hashing was incorrect
        if input.channels.TELEGRAM:
            if input.telegram_id and input.dataCheckString:
                # calculate the hash from check string
                message = (
                    input.dataCheckString.encode("utf-8")
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

                if check_hash == input.hash:
                    # if the hash match
                    # try to get or create a `TelegramProfile` obj
                    try:
                        TelegramProfile.objects.get(id=int(input.telegram_id))

                    except TelegramProfile.DoesNotExist:
                        TelegramProfile.objects.create(
                            id=int(input.telegram_id),
                            user=user,
                        )

                    tracking_list.channels.add(ChannelEnum.TELEGRAM)

                    async_task(
                        "telegram_bot.utils.send_telegram_message",
                        task_name=f"sending-success-connection-{user.pk}",
                        group="telegram_connection",
                        chat_id=int(input.telegram_id),
                        msg=f"Hey {escape_md(user.username)}, "
                        "we connected your telegram with Petroly \\!",
                    )
            else:
                if cerated:
                    # if `TrackingList` is just created remove
                    tracking_list.delete()

                logger.warn(
                    "Issue in setting Telegram ID for user %s: %s %s",
                    user.pk,
                    input.telegram_id,
                    input.dataCheckString,
                )
                return False

        tracking_list.save()
        logger.warn(
            "Request to update channels but nothing changed for user %s: %s",
            user.pk,
            input,
        )

        return True

    @gql.mutation(directives=[IsAuthenticated()])
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

        if len(courses) > 30:
            raise Exception(
                "Sorry you can't track more than 30 sections, consider the Premium plan."
            )

        try:
            # get all `Course` objects or create them
            new_list = []
            for course in courses:
                obj, _ = Course.objects.get_or_create(
                    crn=course.crn,
                    term=course.term,
                    department=course.department,
                )
                new_list.append(obj)

                # always update the status from our cache
                # This will guarantee that the course status is to date
                # before it's being tracked
                course_info = get_course_info(course)
                obj.available_seats = course_info["seatsAvailable"]
                obj.waiting_list_count = course_info["waitAvailable"]
                obj.raw = course_info
                obj.save()

            # clear the old list and set the new one
            tracking_list.courses.set(new_list, clear=True)

        except Exception as exc:
            print(
                f"Error while updating the tracking list for user {user.pk}: ",
                exc,
            )
            return False

        return True
