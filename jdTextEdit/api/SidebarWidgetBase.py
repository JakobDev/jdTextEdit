class SidebarWidgetBase():
    def getName(self) -> str:
        """
        Returns the name that is displayed
        :return: name
        """
        return "Unknown"

    def getID(self) -> str:
        """
        Returns the ID that is used to identify the widget
        :return: id
        """
        return "unknown"