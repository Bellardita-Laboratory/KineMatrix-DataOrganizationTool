import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QTextEdit
)

import regex as re

from UI.Tabs.TabWidget import TabWidget
from UI.UtilsUI import get_user_folder_path, add_input_to_form_layout, MessageType
from FileOrganizer import FileOrganizer

class StructureSelectionTab(TabWidget):
    """
        Tab to select the structure parameters
    """
    # # List of delimiters parameters to ask the user (dictionnary key, display parameter name, parameter default value)
    # delimiters_parameters : dict[tuple[str, str, list[tuple[str,str]]]] = [
    #     ("batch_name_delimiters", "Batch name delimiters (The name of the batch is between 'Start' and 'End' in the file name)\n!- Leave empty for only one batch with the default batch name", [("Start", ''), ("End", '')]),
    #     ("dataset_name_delimiters", "Dataset name delimiters (The name of the dataset is between 'Start' and 'End' in the file name)", [("Start", "CnF_"), ("End", "_Test")]),
    #     ("mouse_name_delimiters", "Mouse name delimiters (The name of the mouse is between 'Start' and 'End' in the file name)", [("Start", "ventral_"), ("End", "_CnF")]),
    #     ("run_name_delimiters", "Run name delimiters (The name of the run is between 'Start' and 'End' in the file name)", [("Start", "Treadmill"), ("End", "DLC")])
    # ]

    structure_str_paramters : list[tuple[str, str, str]] = [
        ("structure_str", """Structure of the file names: use '(' and ')' to capture a group
    A group can be Batch, Dataset, Mouse or Run
         eg: (Batch)_(Dataset)_(Mouse)_(Run)""", "_Mouse(Mouse)_CnF_(Dataset)[_Test]?_(Batch)_[L|l]eft_Run(Run)DLC")
    ]

    # structure_str_paramters : tuple[str, str, str] = (
    #     "structure_str", 
    #     """Structure of the file names: use '(' and ')' to capture a group
    # A group can be Batch, Dataset, Mouse or Run
    #      eg: (Batch)_(Dataset)_(Mouse)_(Run)""", 
    #     "_Mouse(Mouse)_CnF_(Dataset)[_Test]?_(Batch)_[L|l]eft_Run(Run)DLC"
    # )

    # List of parameters names to display in the list widget
    name_list_parameters : list[str] = ["Batch", "Dataset", "Mouse", "Run"]

    def __init__(self, file_organizer:FileOrganizer, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.file_organizer = file_organizer
        self.structure_str_parameters_dict : dict[str, str] = dict()
        self.list_widget_dict : dict[str, QListWidget] = dict()

        self._setup_ui()
    
    def _setup_ui(self):
        """
            Setup the UI of the tab
        """
        v_layout = QVBoxLayout()
        self.setLayout(v_layout)

        ### Delimiters selection
        delimiters_selection_group = QGroupBox("Delimiters")
        delimiters_selection_group.setFlat(True)
        v_layout.addWidget(delimiters_selection_group)

        delimiter_v_layout = QVBoxLayout()
        delimiters_selection_group.setLayout(delimiter_v_layout)

        delimiters_description = QLabel("""Structure supports regular expressions. 
                                        - Use '.' for any character
                                        - Use '*' for repeating the previous character 0 or more times
                                        - Use '+' for repeating the previous character 1 or more times
                                        - Use '?' for repeating the previous character 0 or 1 time
                                        - Use '[' and ']' for specifying a set of characters (eg [0-9] for any digit)
                                        - Use '^' for negating a set of characters (eg [^0-9] for any character that is not a digit)
                                        - Use '\\' to escape special characters
                                        - Use '|' for or (eg 'a|b' for 'a' or 'b')
                                        - Use '^' at the start to specify the start of the string
                                        - Use '$' at the end to specify the end of the string

Examples:
    - If the file name is 'Batch1_Dataset3_Mouse245_Run78', we can use 'Batch(Batch)_Dataset(Dataset)_Mouse(Mouse)_Run(Run)'
        It will find '1' for the batch name, '3' for the dataset name, '245' for the mouse name and '78' for the run name
                                        """
        )
        delimiters_description.setWordWrap(True)
        delimiter_v_layout.addWidget(delimiters_description)

        delimiters_form_layout = QFormLayout()
        delimiter_v_layout.addLayout(delimiters_form_layout)

        structure_str_input_dict = add_input_to_form_layout(delimiters_form_layout, None, StructureSelectionTab.structure_str_paramters, self.structure_str_parameters_dict)

        for _, struture_str_input in structure_str_input_dict.items():
           struture_str_input.textChanged.connect(self.actualize_names)

        # self.structure_str_input = QTextEdit(StructureSelectionTab.structure_str_paramters[2])
        # self._actualize_input_name()
        # self.structure_str_input.setAcceptRichText(True)
        # self.structure_str_input.textChanged.connect(self._actualize_input_name)
        # self.structure_str_input.textChanged.connect(self.actualize_names)
        
        # delimiters_form_layout.addRow(StructureSelectionTab.structure_str_paramters[1], self.structure_str_input)


        ### Names display
        self.name_display_status = QLabel()
        v_layout.addWidget(self.name_display_status, alignment=Qt.AlignCenter)
        self._update_name_display("No issue", MessageType.INFORMATION)

        h_layout = QHBoxLayout()
        v_layout.addLayout(h_layout)

        for name in StructureSelectionTab.name_list_parameters:
            in_v_layout = QVBoxLayout()
            h_layout.addLayout(in_v_layout)

            label = QLabel(name)
            in_v_layout.addWidget(label)

            list_widget = QListWidget()
            self.list_widget_dict[name] = list_widget
            in_v_layout.addWidget(list_widget)

        # Next button
        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self._next_btn_clicked)
        v_layout.addWidget(next_btn)

    def _actualize_input_name(self):
        """
            Actualize the input name display
        """
        new_text = self.structure_str_input.toPlainText()
        print(new_text)
        self.structure_str_parameters_dict[StructureSelectionTab.structure_str_paramters[0]] = new_text

        self.structure_str_input.blockSignals(True)
        self.structure_str_input.setText(new_text)
        self.structure_str_input.blockSignals(False)
        
    def actualize_names(self):
        """
            Actualize the UI of the tab
        """
        # Set the structure parameters in the file organizer
        self._set_file_organizer_structure()

        # Get the associated names
        try:
            associated_names = self.file_organizer.get_names()
        except re.error as e:
            self._update_name_display(f"Error in the regular expression: {e}", MessageType.ERROR)
            return
        else:
            self._update_name_display("No issue", MessageType.INFORMATION)
        
        self._actualize_names_display(associated_names)

    def _update_name_display(self, message:str, message_type:MessageType):
        """
            Display the error message in the name display status
        """
        self.name_display_status.setText(message)

        if message_type == MessageType.ERROR:
            self.name_display_status.setStyleSheet("font-weight: bold; color: red")
        elif message_type == MessageType.INFORMATION:
            self.name_display_status.setStyleSheet("font-weight: bold")
        elif message_type == MessageType.WARNING:
            self.name_display_status.setStyleSheet("font-weight: bold; color: orange")

    def _actualize_names_display(self, associated_names: list[tuple[str, str, str, str]]):
        """
            Actualize the display of the names in the tab
        """
        # Separate the names in different lists
        batch_names = [batch_name for batch_name, _, _, _ in associated_names]
        dataset_names = [dataset_name for _, dataset_name, _, _ in associated_names]
        mouse_names = [mouse_name for _, _, mouse_name, _ in associated_names]
        run_names = [run_name for _, _, _, run_name in associated_names]

        # Remove duplicates
        batch_names = list(set(batch_names))
        dataset_names = list(set(dataset_names))
        mouse_names = list(set(mouse_names))
        run_names = list(set(run_names))

        self._actualize_list_widget("Batch", batch_names)
        self._actualize_list_widget("Dataset", dataset_names)
        self._actualize_list_widget("Mouse", mouse_names)
        self._actualize_list_widget("Run", run_names)

    def _actualize_list_widget(self, name:str, names_list:list[str]):
        """
            Actualize the content of the list widget with the given name
        """
        list_widget = self.list_widget_dict[name]
        list_widget.clear()
        list_widget.addItems(names_list)

    def _next_btn_clicked(self):
        """
            Function called when the user clicks on the next button
        """
        # Set the structure parameters in the file organizer
        self._set_file_organizer_structure()

        # Emit the signal to change the tab
        self.change_tab_signal.emit()

    def _set_file_organizer_structure(self):
        """
            Set the structure parameters in the file organizer
        """
        # Save the structure parameters
        self.file_organizer.set_structure_str_parameters(**self.structure_str_parameters_dict)