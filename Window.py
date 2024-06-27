import os
from pathlib import Path
from PySide6.QtCore import QSize, Qt, Signal, QThread, QLocale, QSortFilterProxyModel, QStringListModel
from PySide6.QtGui import QPixmap, QImage, QDoubleValidator, QIntValidator, QValidator
from PySide6.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QPushButton, 
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QSlider, 
    QLabel, 
    QListWidget,
    QListWidgetItem,
    QStackedLayout,
    QAbstractItemView,
    QCheckBox,
    QSpacerItem,
    QTabWidget,
    QFormLayout,
    QFileDialog,
    QGroupBox,
    QStyle,
    QLineEdit,
    QMessageBox,
    QComboBox,
    QCompleter,
    QSplitter
    )

from FileOrganizer import FileOrganizer
from UtilsUI import add_input_to_form_layout

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self, window_title:str, min_win_size:QSize = QSize(1200,487)):
        super().__init__()
        self.setMinimumSize(min_win_size)        
        self.setWindowTitle(window_title)

        # Dictionary to store the parameters selected by the user
        self.file_organizer_parameters_dict : dict[str, None | str | os.PathLike] = dict()
        self.organize_file_parameters_dict : dict[str, str | os.PathLike] = dict()

        # Main layout
        v_layout = QVBoxLayout()


        ### Folder selection
        folder_selection_group = QGroupBox("Folders selection")
        folder_selection_group.setFlat(True)
        v_layout.addWidget(folder_selection_group)

        folder_form_layout = QFormLayout()
        folder_selection_group.setLayout(folder_form_layout)

        self.folder_selection_parameters = [
            ("data_folder_path", "Data folder", os.path.join('E:', 'Treadmill - no stimulation')),
            ("target_folder_path", "Target folder", os.path.join('E:', 'NewTreadmilTest'))
            ]

        # Instantiate the folder selection widgets
        for key_name, display_str, default_value in self.folder_selection_parameters:
            self.organize_file_parameters_dict[key_name] = default_value

            folder_layout = self._create_select_folder_layout(key_name, default_value, self.organize_file_parameters_dict)
            folder_form_layout.addRow(display_str, folder_layout)

        ### Parameters selection
        parameters_selection_group = QGroupBox("Parameters")
        parameters_selection_group.setFlat(True)
        v_layout.addWidget(parameters_selection_group)

        parameters_form_layout = QFormLayout()
        parameters_selection_group.setLayout(parameters_form_layout)

        # TODO: pass these values as parameters instead of hardcoding
        # List of single value parameters to ask the user (dictionnary key, display parameter name, parameter default value)
        single_value_parameters : list[tuple[str, str, float]] = [ 
            ("csv_extension", "CSV extension", ".csv"),
            ("video_extension", "Video extension", ".mp4"),
            ("side_folder_name", "Side folder name", "side_view_analysis"),
            ("ventral_folder_name", "Ventral folder name", "ventral_view_analysis"),
            ("video_folder_name", "Video folder name", "Video")
        ]

        # Adds these parameters to the form layout
        add_input_to_form_layout(parameters_form_layout, None, single_value_parameters, self.organize_file_parameters_dict)

        single_value_parameters : list[tuple[str, str, float]] = [
            ("default_batch_name", "Default batch name", "Batch"),
            ("side_keyword", "Side keyword", "sideview"),
            ("ventral_keyword", "Ventral keyword", "ventralview")
        ]

        # Adds these parameters to the form layout
        add_input_to_form_layout(parameters_form_layout, None, single_value_parameters, self.file_organizer_parameters_dict)

        ### Delimiters selection
        delimiters_selection_group = QGroupBox("Delimiters")
        delimiters_selection_group.setFlat(True)
        v_layout.addWidget(delimiters_selection_group)

        delimiters_form_layout = QFormLayout()
        delimiters_selection_group.setLayout(delimiters_form_layout)

        # TODO: pass these values as parameters instead of hardcoding
        # List of vector value parameters to ask the user (dictionnary key, display parameter name, parameter default value)
        vector_value_parameters = [
            ("dataset_name_delimiters", "Dataset name delimiters", [("Start", "CnF_"), ("End", "_Test")]),
            ("mouse_name_delimiters", "Mouse name delimiters", [("Start", "ventral_"), ("End", "_CnF")]),
            ("run_name_delimiters", "Run name delimiters", [("Start", "Treadmill"), ("End", "DLC")]),
            ("batch_name_delimiters", "Batch name delimiters", [("Start", ''), ("End", '')])
        ]

        # TODO: Allow the user to click to chose the coord
        # Adds these parameters to the form layout
        add_input_to_form_layout(delimiters_form_layout, None, vector_value_parameters, self.file_organizer_parameters_dict)

        ### Organize button
        organize_btn = QPushButton("Organize Files")
        organize_btn.clicked.connect(self._organize_btn_clicked)
        v_layout.addWidget(organize_btn)

        widget = QWidget()
        widget.setLayout(v_layout)
        self.setCentralWidget(widget)

    def _create_select_folder_layout(self, filepath_dict_key:str, default_value:str, dictionary:dict[str, os.PathLike]):
        """
            Returns the layout for a folder selection widget,
            Calling self.select_folder when a new folder is selected
        """
        folder_layout = QHBoxLayout()
        folder_label = QLabel(default_value)
        folder_btn = QPushButton("Select folder")

        folder_btn.clicked.connect(
            lambda : self._select_folder(folder_label, filepath_dict_key, dictionary)
        )
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(folder_btn)

        return folder_layout
        
    def _select_folder(self, label:QLabel, filepath_dict_key:str, dictionary:dict[str, os.PathLike]):
        """
            Asks the user to select a directory, display the result in the label and saves it in self.parameters_dict with the key filepath_dict_key
        """
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        label.setText(file)
        dictionary[filepath_dict_key] = file

    def _organize_btn_clicked(self):
        print(self.file_organizer_parameters_dict)
        print(self.organize_file_parameters_dict)

        batch_name_delimiters = self.file_organizer_parameters_dict["batch_name_delimiters"]
        if batch_name_delimiters[0] == '' and batch_name_delimiters[1] == '':
            self.file_organizer_parameters_dict["batch_name_delimiters"] = None

        organizer = FileOrganizer(**self.file_organizer_parameters_dict)

        organizer.organize_files(**self.organize_file_parameters_dict)

        # Show a message box to inform the user that the files have been organized
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Files have been organized")
        msg.setWindowTitle("Information")
        msg.exec()

if __name__ == "__main__":
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication([])

    # Create a Qt widget, which will be our window.
    window = MainWindow(window_title="Features Analyzer")
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()

    # Your application won't reach here until you exit and the event
    # loop has stopped.