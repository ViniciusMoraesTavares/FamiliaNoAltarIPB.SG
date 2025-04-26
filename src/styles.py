from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

class AppStyles:
    PRIMARY_COLOR = "#4CAF50"
    PRIMARY_DARK = "#388E3C"
    PRIMARY_LIGHT = "#A5D6A7"
    BACKGROUND_COLOR = "#FFFFFF"
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    
    @staticmethod
    def button_style(variant="primary"):
        styles = {
            "primary": f"""
                QPushButton {{
                    background-color: {AppStyles.PRIMARY_COLOR};
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {AppStyles.PRIMARY_DARK};
                }}
                QPushButton:disabled {{
                    background-color: {AppStyles.PRIMARY_LIGHT};
                    color: #F1F8E9;
                }}
            """,
            "danger": """
                QPushButton {
                    background-color: #EF5350;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E53935;
                }
            """
        }
        return styles.get(variant, styles["primary"])
    
    @staticmethod
    def card_style():
        return """
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """
    
    @staticmethod
    def input_style():
        return """
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: #FAFAFA;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                background: white;
            }
        """
    
    @staticmethod
    def get_shadow_effect():
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        return shadow 