import AvailableDumpsLabel
import ClearAvailableDumpsButton
import DownloaderComboBox
import DownloadLabel
import DownloadSelectionButton
import DumpListTreeView
import FilterButton
import FilterByDateComboBox
import FilterByDateLabel
import FilterByMirrorComboBox
import FilterByMirrorLabel
import FilterBySizeLabel
import FilterByWikiFarmLabel
import LoadAvailableDumpsButton
import NotDownloadLabel
import SizeComboBox
import TreeScrollBar
import WikiUrlLabel
from PySide6.QtWidgets import QBoxLayout


class DownloaderBoxLayout(QBoxLayout):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(parent)
        self.wiki_url_label = WikiUrlLabel(self, text="Wiki URL:")
        self.available_dumps_label = AvailableDumpsLabel(self)
        self.downloaded_label = DownloadLabel(self)
        self.not_downloaded_label = NotDownloadLabel(self)
        self.filter_by_wikifarm_label = FilterByWikiFarmLabel(self)
        self.downloader_combo_box = DownloaderComboBox(self)
        self.filter_by_size_label = FilterBySizeLabel(self)
        self.size_combo_box = SizeComboBox(self)
        self.filter_by_date_label = FilterByDateLabel(self)
        self.filter_by_date_combo_box = FilterByDateComboBox(self)
        self.filter_by_mirror_menu = FilterByMirrorComboBox(self)
        self.tree_scroll_bar = TreeScrollBar(self)
        self.tree_view = DumpListTreeView(self)
        self.load_available_dumps_button = LoadAvailableDumpsButton(self)
        self.download_selection_button = DownloadSelectionButton(self)
        self.clear_available_dumps_button = ClearAvailableDumpsButton(self)
        self.filter_button = FilterButton(self)
        self.filter_by_mirror_label = FilterByMirrorLabel(self)
        # end tabs
