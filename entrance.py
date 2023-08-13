from core.ApplicationManager import ApplicationWindowManager
from core.Profile import Profile
from core.UI.MainMenu import MainMenu
from core.UI.InsertOrderablePartsMenu import InsertOrderablePartsMenu


if __name__ == '__main__':
    manager = ApplicationWindowManager()
    manager.add_window('main_menu', MainMenu)
    manager.add_window('orderable_part', InsertOrderablePartsMenu)
    manager.start()