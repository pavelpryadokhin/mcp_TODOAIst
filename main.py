from mcp.server.fastmcp import FastMCP
from caldav_tool.mcp_service import CalDAVTool


mcp = FastMCP("caldav_calendar")


# Add the CalDAVTool to the server
caldav_tool = CalDAVTool()

mcp.add_tool(caldav_tool.create_calendar)
mcp.add_tool(caldav_tool.create_event)
mcp.add_tool(caldav_tool.delete_calendar)
mcp.add_tool(caldav_tool.delete_event)
mcp.add_tool(caldav_tool.get_calendar)
mcp.add_tool(caldav_tool.get_event)
mcp.add_tool(caldav_tool.list_calendars)
mcp.add_tool(caldav_tool.list_events)
mcp.add_tool(caldav_tool.update_calendar)
mcp.add_tool(caldav_tool.update_event)


if __name__ == "__main__":
    print("CalDAV MCP server is running...")
    mcp.run()