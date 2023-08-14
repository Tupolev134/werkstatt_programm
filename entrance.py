from core.ApplicationManager import ApplicationWindowManager
from core.Profile import Profile
from core.UI.InsertOrder import InsertOrderPage
from core.UI.InsertOrderablePartsRaw import InsertOrderablePartsRaw
from core.UI.MainMenu import MainMenu
from core.UI.InsertOrderablePartsMenu import InsertOrderablePartsMenu


if __name__ == '__main__':
    manager = ApplicationWindowManager()
    manager.add_window('main_menu', MainMenu)
    manager.add_window('insert_order', InsertOrderPage)
    manager.add_window('orderable_part', InsertOrderablePartsMenu)
    manager.add_window('orderable_part_raw', InsertOrderablePartsRaw)
    manager.start()