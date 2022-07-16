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

    # wiki_url_label: WikiUrlLabel
    # available_dumps_label: AvailableDumpsLabel
    # downloaded_label: DownloadLabel
    # not_downloaded_label: NotDownloadLabel
    # filter_by_wikifarm_label: FilterByWikiFarmLabel
    # downloader_combo_box: DownloaderComboBox
    # filter_by_size_label: FilterBySizeLabel
    # size_combo_box: SizeComboBox
    # filter_by_date_label: FilterByDateLabel
    # filter_by_date_combo_box: FilterByDateComboBox
    # filter_by_mirror_menu: FilterByMirrorComboBox
    # tree_scroll_bar: TreeScrollBar
    # tree_view: DumpListTreeView
    # load_available_dumps_button: LoadAvailableDumpsButton
    # download_selection_button: DownloadSelectionButton
    # clear_available_dumps_button: ClearAvailableDumpsButton
    # filter_button: FilterButton
    # filter_by_mirror_label: FilterByMirrorLabel

    def __init__(self, parent):

        super(parent)

        self.wiki_url_label: WikiUrlLabel = WikiUrlLabel(self)
        self.insertItem(self.wiki_url_label)

        self.available_dumps_label = AvailableDumpsLabel(self)
        self.insertItem(self.available_dumps_label)

        self.downloaded_label = DownloadLabel(self)
        self.insertItem(self.downloaded_label)

        self.not_downloaded_label = NotDownloadLabel(self)
        self.insertItem(self.not_downloaded_label)

        self.filter_by_wikifarm_label = FilterByWikiFarmLabel(self)
        self.insertItem(self.filter_by_wikifarm_label)

        self.downloader_combo_box = DownloaderComboBox(self)
        self.insertItem(self.downloader_combo_box)

        self.filter_by_size_label = FilterBySizeLabel(self)
        self.insertItem(self.filter_by_size_label)

        self.size_combo_box = SizeComboBox(self)
        self.insertItem(self.size_combo_box)

        self.filter_by_date_label = FilterByDateLabel(self)
        self.insertItem(self.filter_by_date_label)

        self.filter_by_date_combo_box = FilterByDateComboBox(self)
        self.insertItem(self.filter_by_date_combo_box)

        self.filter_by_mirror_menu = FilterByMirrorComboBox(self)
        self.insertItem(self.filter_by_mirror_menu)

        self.tree_scroll_bar = TreeScrollBar(self)
        self.insertItem(self.tree_scroll_bar)

        self.tree_view = DumpListTreeView(self)
        self.insertItem(self.tree_view)

        self.load_available_dumps_button = LoadAvailableDumpsButton(self)
        self.insertItem(self.load_available_dumps_button)

        self.download_selection_button = DownloadSelectionButton(self)
        self.insertItem(self.download_selection_button)

        self.clear_available_dumps_button = ClearAvailableDumpsButton(self)
        self.insertItem(self.clear_available_dumps_button)

        self.filter_button = FilterButton(self)
        self.insertItem(self.filter_button)

        self.filter_by_mirror_label = FilterByMirrorLabel(self)
        self.insertItem(self.filter_by_mirror_label)

        # end tabs
