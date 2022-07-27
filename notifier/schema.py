"""
This module is to define the GraphQL queries and mutations
of the `notifier` app.
"""

import dataclasses
from typing import List
import hmac;
import hashlib;
import os
from strawberry.scalars import JSON
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import IsAuthenticated
from django_q.tasks import async_task

from .utils import fetch_data, get_course_info
from .models import TrackingList, Course, ChannelEnum
from .types import CourseInput, TermType, ChannelsType, PreferencesInput





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
    def tracking_list_channels(self, info: Info) -> ChannelsType:
        """Get the user's tracking list tracking_list_channels."""

        user = info.context.request.user

        res = {}
        for name in ChannelEnum.names:
            res |= {name: ChannelEnum[name] in user.tracking_list.channels}

        return ChannelsType(**res)

    @gql.field(directives=[IsAuthenticated()])
    def tracked_courses(self, info: Info) -> JSON:
        """get all tracked courses' CRNs by the
        current logged in user.

        Returns:
            List[CourseType]: List of courses CRNs
        """

        user = info.context.request.user
        tracking_list, created = TrackingList.objects.get_or_create(user=user)
        
        if created:
            return []

        result = []
        for course in tracking_list.courses.all():
            for raw_course in fetch_data(course.term, course.department):
                if course.crn == raw_course["crn"]:
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

        raw = fetch_data(term, department)
        result = []
        for course in raw:
            if (
                title.lower() in course["course_number"].lower()
                or title.lower() in course["course_title"].lower()
            ):
                result.append(course)
        return result


@gql.type
class Mutation:
    """Main entry of all Mutation types of `notifier` app."""
    ## ! to perform authorization we need to pas both the data-check-string, and the hash as well
    @gql.mutation(directives=[IsAuthenticated()])
    def update_tracking_list_channels(
        self, info: Info, input: PreferencesInput
    ) -> bool:
        """To update user's tracking list preferences"""

        user = info.context.request.user
        channels = dataclasses.asdict(input.channels)
        print(input)

        user.tracking_list.channels.clear()
        for channel, checked in channels.items():
            if checked:
                user.tracking_list.channels.append(ChannelEnum[channel])
            else:
                try:
                    user.tracking_list.channels.remove(ChannelEnum[channel])
                except ValueError:
                    pass
        
        user.tracking_list.save()
        # ! check for the hashing and return false to the caller if the hashing was incorrect
        # ! if the telegram channel was already check, we do not require hashing, to prevent errors
        secret_key = hashlib.sha256( os.environ.get("TELEGRAM_BOT_TOKEN").encode("utf-8")).digest()
        print(input.dataCheckString)
        message = input.dataCheckString.encode('utf-8').decode('unicode-escape').encode('ISO-8859-1')
        var = hmac.new(key = (secret_key), msg = message, digestmod= hashlib.sha256).hexdigest();  # type: ignore
        print(var == input.hash)  # type: ignore
        print(var)
        print(input.hash)

        return True

    @gql.mutation(directives=[IsAuthenticated()])
    def update_tracking_list(
        self, info: Info, courses: List[CourseInput]
    ) -> bool:
        """Add all `courses` to the user's tracking list
        then update each course status from the cache.

        Args:
            info (Info): given by GraphQL
            courses (List[CourseInput]): A list of CourseInput

        Returns:
            bool: A success flag
        """
        user = info.context.request.user
        tracking_list = TrackingList.objects.get_or_create(user=user)[0]

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
                obj.available_seats = course_info["available_seats"]
                obj.waiting_list_count = course_info["waiting_list_count"]
                obj.save()

            # clear the old list and set the new one
            tracking_list.courses.set(new_list, clear=True)

        except Exception as exc:
            print(exc)
            return False

        return True
