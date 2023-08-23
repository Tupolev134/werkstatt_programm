from core.ApplicationManager import ApplicationWindowManager
from core.UI.insert_pages.InsertOrder import InsertOrderPage
from core.UI.insert_pages.InsertOrderablePartsRaw import InsertOrderablePartsRaw
from core.UI.MainMenu import MainMenu
from core.UI.insert_pages.InsertOrderablePartsMenu import InsertOrderablePartsMenu


if __name__ == '__main__':
    manager = ApplicationWindowManager()
    manager.add_window('main_menu', MainMenu)
    manager.add_window('insert_order', InsertOrderPage)
    manager.add_window('orderable_part', InsertOrderablePartsMenu)
    manager.add_window('orderable_part_raw', InsertOrderablePartsRaw)
    manager.start()