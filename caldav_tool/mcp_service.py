import os
import sys
# Ensure the project root is in sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from typing import List, Optional, Any, Dict

from caldav_tool.caldav_client import CalDAVClient
from caldav_tool.schemas import CalendarSchema, EventSchema
from caldav_tool import settings
import logging

class CalDAVTool:
    """
    MCP Tool for interacting with CalDAV calendars.
    """
    def __init__(self):
        try:
            self.client = CalDAVClient(
                url=settings.CALDAV_URL,
                username=settings.CALDAV_USERNAME,
                password=settings.CALDAV_PASSWORD
            )
        except ConnectionError as e:
            logging.error(f"Failed to initialize CalDAVTool due to connection error: {e}")
            raise

    def _to_calendar_schema(self, calendar) -> CalendarSchema:
        """Converts a caldav Calendar object to a CalendarSchema."""
        return CalendarSchema(
            id=calendar.id,
            name=getattr(calendar, 'name', str(getattr(calendar, 'url', ''))),
            description=str(getattr(calendar, 'description', '')),
            url=str(getattr(calendar, 'url', ''))
        )

    def _to_event_schema(self, event) -> EventSchema:
        """Converts a caldav Event object to an EventSchema."""
        v_event = event.vobject_instance.vevent
        description_attr = getattr(v_event, 'description', None)
        description = description_attr.value if description_attr else None
        return EventSchema(
            id=v_event.uid.value,
            summary=v_event.summary.value,
            start_time=v_event.dtstart.value,
            end_time=v_event.dtend.value,
            description=description
        )

    def list_calendars(self) -> List[CalendarSchema]:
        """
        Retrieves a list of all calendars available to the authenticated user.

        Returns:
            A list of CalendarSchema objects, each representing a calendar.
        """
        calendars = self.client.list_calendars()
        return [self._to_calendar_schema(cal) for cal in calendars if cal]

    def create_calendar(self, name: str, description: Optional[str] = None) -> Optional[CalendarSchema]:
        """
        Creates a new calendar on the CalDAV server.

        Args:
            name: The name for the new calendar.
            description: An optional description for the calendar.

        Returns:
            A CalendarSchema object for the newly created calendar, or None if creation fails.
        """
        calendar = self.client.create_calendar(name=name, description=description)
        return self._to_calendar_schema(calendar) if calendar else None

    def get_calendar(self, calendar_id: str) -> Optional[CalendarSchema]:
        """
        Retrieves a specific calendar by its unique ID.

        Args:
            calendar_id: The ID of the calendar to retrieve.

        Returns:
            A CalendarSchema object for the found calendar, or None if not found.
        """
        calendar = self.client.get_calendar(calendar_id=calendar_id)
        return self._to_calendar_schema(calendar) if calendar else None

    def update_calendar(self, calendar_id: str, name: str) -> Optional[CalendarSchema]:
        """
        Updates the name of an existing calendar.

        Args:
            calendar_id: The ID of the calendar to update.
            name: The new name for the calendar.

        Returns:
            A CalendarSchema object for the updated calendar, or None if the update fails.
        """
        calendar = self.client.update_calendar(calendar_id=calendar_id, name=name)
        return self._to_calendar_schema(calendar) if calendar else None

    def delete_calendar(self, calendar_id: str) -> bool:
        """
        Deletes a calendar from the server.

        Args:
            calendar_id: The ID of the calendar to delete.

        Returns:
            True if the calendar was deleted successfully, False otherwise.
        """
        return self.client.delete_calendar(calendar_id=calendar_id)

    def list_events(self, calendar_id: str, start_date: datetime, end_date: datetime) -> List[EventSchema]:
        """
        Lists all events within a specified date range for a given calendar.

        Args:
            calendar_id: The ID of the calendar to search for events.
            start_date: The start of the date range.
            end_date: The end of the date range.

        Returns:
            A list of EventSchema objects representing the events found.
        """
        events = self.client.list_events(calendar_id=calendar_id, start_date=start_date, end_date=end_date)
        return [self._to_event_schema(event) for event in events if event]

    def create_event(self, calendar_id: str, summary: str, start: datetime, end: datetime,
                     description: Optional[str] = "") -> Optional[EventSchema]:
        """
        Creates a new event in a specified calendar.

        Args:
            calendar_id: The ID of the calendar where the event will be created.
            summary: A brief summary or title for the event.
            start: The start time of the event.
            end: The end time of the event.
            description: An optional detailed description for the event.

        Returns:
            An EventSchema object for the newly created event, or None if creation fails.
        """
        event = self.client.create_event(calendar_id=calendar_id, summary=summary, start=start, end=end, description=description)
        return self._to_event_schema(event) if event else None

    def get_event(self, calendar_id: str, event_uid: str) -> Optional[EventSchema]:
        """
        Retrieves a specific event by its unique ID (UID) from a calendar.

        Args:
            calendar_id: The ID of the calendar containing the event.
            event_uid: The UID of the event to retrieve.

        Returns:
            An EventSchema object for the found event, or None if not found.
        """
        event = self.client.get_event(calendar_id=calendar_id, event_uid=event_uid)
        return self._to_event_schema(event) if event else None

    def update_event(self, calendar_id: str, event_uid: str, updates: Dict[str, Any]) -> Optional[EventSchema]:
        """
        Updates an existing event with new information.

        Args:
            calendar_id: The ID of the calendar containing the event.
            event_uid: The UID of the event to update.
            updates: A dictionary of properties to update on the event.

        Returns:
            An EventSchema object for the updated event, or None if the update fails.
        """
        event = self.client.update_event(calendar_id=calendar_id, event_uid=event_uid, updates=updates)
        return self._to_event_schema(event) if event else None

    def delete_event(self, calendar_id: str, event_uid: str) -> bool:
        """
        Deletes an event from a calendar.

        Args:
            calendar_id: The ID of the calendar containing the event.
            event_uid: The UID of the event to delete.

        Returns:
            True if the event was deleted successfully, False otherwise.
        """
        return self.client.delete_event(calendar_id=calendar_id, event_uid=event_uid)

    # Add other high-level methods for the agent to use 