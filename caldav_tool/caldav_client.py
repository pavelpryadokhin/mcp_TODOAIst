import logging
import uuid
import vobject
from datetime import datetime, timedelta
from typing import Any, List, Optional

import caldav
from caldav.lib import error
from caldav.elements import dav
from caldav.objects import Calendar, Event

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CalDAVClient:
    """
    A client for interacting with a CalDAV server.
    """

    def __init__(self, url: str, username: str, password: str):
        if not all([url, username, password]):
            raise ValueError("URL, username, and password cannot be empty.")
        try:
            self.client = caldav.DAVClient(url=url, username=username, password=password)
            self.principal = self.client.principal()
        except error.DAVError as e:
            logging.error(f"Failed to connect or authenticate with CalDAV server: {e}")
            raise ConnectionError(f"CalDAV connection failed: {e}") from e

    def list_calendars(self) -> List[Calendar]:
        """
        Lists all available calendars.
        """
        try:
            return self.principal.calendars()
        except error.DAVError as e:
            logging.error(f"Failed to list calendars: {e}")
            raise ConnectionError(f"Could not retrieve calendars: {e}") from e

    def create_calendar(self, name: str, description: Optional[str] = None) -> Optional[Calendar]:
        """Creates a new calendar."""

        try:
            calendar_id = str(uuid.uuid4())
            new_calendar = self.principal.make_calendar(name=name, cal_id=calendar_id)

            if description:
                new_calendar.set_properties([caldav.lib.namespace.dav.Description(description)])

            return new_calendar
        except error.DAVError as e:
            logging.error(f"Failed to create calendar '{name}': {e}")
            return None

    def get_calendar(self, calendar_id: str) -> Optional[Calendar]:
        """Retrieves a specific calendar by its ID."""
        if not calendar_id:
            logging.error("Calendar ID cannot be empty.")
            return None
        try:
            return self.principal.calendar(cal_id=calendar_id)
        except error.NotFoundError:
            logging.warning(f"Calendar with ID '{calendar_id}' not found.")
            return None
        except error.DAVError as e:
            logging.error(f"Failed to retrieve calendar '{calendar_id}': {e}")
            return None

    def update_calendar(self, calendar_id: str, name: str) -> Optional[Calendar]:
        """Updates a calendar's name."""
        if not name:
            logging.error("New calendar name cannot be empty.")
            return None
        calendar = self.get_calendar(calendar_id)
        if not calendar:
            return None
        try:
            calendar.set_properties([dav.DisplayName(name)])
            return calendar
        except error.DAVError as e:
            logging.error(f"Failed to update calendar '{calendar_id}': {e}")
            return None

    def delete_calendar(self, calendar_id: str) -> bool:
        """Deletes a calendar by its ID. Returns True on success."""
        calendar = self.get_calendar(calendar_id)
        if not calendar:
            return False
        try:
            calendar.delete()
            return True
        except error.DAVError as e:
            logging.error(f"Failed to delete calendar '{calendar_id}': {e}")
            return False

    def list_events(self, calendar_id: str, start_date: datetime, end_date: datetime) -> List[Event]:
        """Lists events in a calendar within a date range."""
        calendar = self.get_calendar(calendar_id)
        if not calendar:
            return []
        try:
            return calendar.date_search(start=start_date, end=end_date, expand=True)
        except error.DAVError as e:
            logging.error(f"Failed to list events for calendar '{calendar_id}': {e}")
            return []

    def create_event(self, calendar_id: str, summary: str, start: datetime, end: datetime,
                     description: Optional[str] = "") -> Optional[Event]:
        """Creates a new event using the vobject library."""
        calendar = self.get_calendar(calendar_id)
        if not calendar or not summary:
            logging.error("Calendar must exist and summary cannot be empty.")
            return None

        vcal = vobject.iCalendar()
        vevent = vcal.add('vevent')
        vevent.add('uid').value = str(uuid.uuid4())
        vevent.add('dtstamp').value = datetime.utcnow()
        vevent.add('dtstart').value = start
        vevent.add('dtend').value = end
        vevent.add('summary').value = summary
        if description:
            vevent.add('description').value = description

        try:
            return calendar.save_event(vcal.serialize())
        except error.DAVError as e:
            logging.error(f"Failed to create event in calendar '{calendar_id}': {e}")
            return None

    def get_event(self, calendar_id: str, event_uid: str) -> Optional[Event]:
        """Retrieves a specific event by its UID."""
        calendar = self.get_calendar(calendar_id)
        if not calendar or not event_uid:
            return None
        try:
            return calendar.event_by_uid(uid=event_uid)
        except error.NotFoundError:
            logging.warning(f"Event with UID '{event_uid}' not found in calendar '{calendar_id}'.")
            return None
        except error.DAVError as e:
            logging.error(f"Failed to retrieve event '{event_uid}': {e}")
            return None

    def delete_event(self, calendar_id: str, event_uid: str) -> bool:
        """Deletes an event by its UID. Returns True on success."""
        event = self.get_event(calendar_id, event_uid)
        if not event:
            return False
        try:
            event.delete()
            return True
        except error.DAVError as e:
            logging.error(f"Failed to delete event '{event_uid}': {e}")
            return False

    def update_event(self, calendar_id: str, event_uid: str, updates: dict[str, Any]) -> Optional[Event]:
        """Updates an event's properties using vobject."""
        event = self.get_event(calendar_id, event_uid)
        if not event:
            return None
        try:
            v_event = event.vobject_instance.vevent
            for key, value in updates.items():
                if hasattr(v_event, key):
                    getattr(v_event, key).value = value
                else:
                    v_event.add(key).value = value

            event.save()
            return event
        except Exception as e:
            logging.error(f"Failed to update event '{event_uid}': {e}")
            return None


def test_caldav_locally():
    """A function to test the CalDAVClient against a local server."""
    from caldav_tool import settings

    logging.info("--- Starting CalDAV Client Test ---")
    try:
        client = CalDAVClient(url='https://caldav.yandex.ru', username='pavel.pryadohin',
                              password='fsvdlszzfmnjapvv')
    except ConnectionError as e:
        logging.error(f"Stopping test due to connection failure: {e}")
        return

    logging.info(f"Connected to principal: {client.principal}")
    cal_id = None
    try:
        from datetime import datetime
        start_date = datetime.strptime('2025-06-28 23:59', "%Y-%m-%d %H:%M")
        end_date = datetime.strptime('2025-06-30 23:59', "%Y-%m-%d %H:%M")
        # Create Calendar
        calendar_name = f"new-name"
        calendar_desc = "A test calendar for our client"
        logging.info(f"Creating calendar: {calendar_name}")
        # calendar = client.create_calendar(name=calendar_name, description=calendar_desc)
        calendar = client.list_calendars()[0].id

        event=client.list_events(calendar,start_date=start_date, end_date=end_date)
        # print(client.create_event(calendar,summary="test_event",
        #                           start=start_date, end=end_date,description="test_description"))
        print(event[0].id)

        ical = vobject.readOne(event[0].data)
        uid = ical.vevent.uid.value
        summary = ical.vevent.summary.value

        print("UID:", uid)
        print("Summary:", summary)
        print(client.update_event(calendar,ical.vevent.uid.value,{'summary':"test_event_2"}))
        # cal_id = calendar.id
        logging.info(f"Calendar created with ID {cal_id}")
        print(client.delete_event(calendar,uid))
        print(client.list_events(calendar,start_date=start_date, end_date=end_date))
        print(client.delete_calendar(calendar))

    except AssertionError as e:
        logging.error(f"Assertion FAILED: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during testing: {e}", exc_info=True)

    logging.info("--- CalDAV Client Test Finished ---")


if __name__ == "__main__":
    test_caldav_locally() 