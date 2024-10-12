from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QLineEdit, QStackedWidget, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout,  QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QSize
import sys
import random
import os

class Cell(QPushButton):
    rightClicked = pyqtSignal()
    def __init__(self, row, col):
        super().__init__()
        self.mine = False
        self.x = col
        self.y = row
        self.isClicked = False
        self.isMarked = False

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            super().mousePressEvent(event)
    

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.initBody()
    
    def initBody(self):
        vertLayout = QVBoxLayout()
        vertLayout.setAlignment(Qt.AlignCenter)
        vertLayout.setContentsMargins(100, 0, 100, 0)

        self.label = QLabel('Settings'); self.label.setStyleSheet('font-size: 30px')
        self.label.setAlignment(Qt.AlignCenter)


        self.bombsAmountText = QLineEdit(); self.bombsAmountText.setPlaceholderText('Enter amount of bombs')
        self.bombsAmountText.setMinimumSize(160, 20)
        self.boardSizeText = QLineEdit(); self.boardSizeText.setPlaceholderText('Enter board size (max 30)')    
        self.boardSizeText.setMinimumSize(160, 20) 

        self.b1 = QPushButton('Start'); self.b1.setStyleSheet('font-size: 30px')
        self.b1.clicked.connect(self.started)
        
        vertLayout.addWidget(self.label)
        vertLayout.addWidget(self.bombsAmountText)
        vertLayout.addWidget(self.boardSizeText)
        vertLayout.addWidget(self.b1)

        self.setLayout(vertLayout)


    def started(self):
        try:
            self.bombsAmount = float(self.bombsAmountText.text())
            self.boardSize = float(self.boardSizeText.text())
            if self.bombsAmount >= self.boardSize**2 or self.boardSize > 30:
                int('ValueError')
            if self.bombsAmount == int(self.bombsAmount) and self.boardSize == int(self.boardSize):
                game = Minesweeper(self.bombsAmount, self.boardSize)
                win.addWidget(game)
                win.setCurrentIndex(win.currentIndex()+1)
                self.label.setText('Settings')
        except ValueError:
            self.label.setText('Incorrent data')
            self.bombsAmountText.clear()
            self.boardSizeText.clear()
            self.label.adjustSize()
  

class Minesweeper(QWidget):
    def __init__(self, bombsAmount, boardSize):
        super().__init__()
        self.bombsAmount = int(bombsAmount)
        self.boardSize = int(boardSize)
        self.mineSet = False
        self.initBody()

    def initBody(self):
        bodyLayout = QVBoxLayout()
        boardLayout = QGridLayout()
        infoLayout = QHBoxLayout()

        self.title = QLabel('Game'); self.title.setStyleSheet('font-size: 30px')
        self.bombsLeft = self.bombsAmount
        self.bombCounter = QLabel(f'Bombs Left: {self.bombsLeft}'); self.bombCounter.setStyleSheet('font-size: 18px')
        self.cellsLeft = self.boardSize**2
        self.cellCounter = QLabel(f'Cells Left: {self.cellsLeft}'); self.cellCounter.setStyleSheet('font-size: 18px')

        self.cellList = []
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                cell = Cell(row, col)
                cell.clicked.connect(self.clickedCell)
                cell.rightClicked.connect(self.rightClick)
                cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                cell.setMinimumSize(30, 30)
                cell.setMaximumSize(50, 50)
                self.cellList.append(cell)
                boardLayout.addWidget(cell, row, col)
                boardLayout.setColumnStretch(col, 1)
            boardLayout.setRowStretch(row, 1)

        boardLayout.setSpacing(0)
        boardLayout.setAlignment(Qt.AlignCenter)
        boardLayout.setContentsMargins(10, 10, 10, 10)

        infoLayout.addWidget(self.bombCounter)
        infoLayout.addStretch()
        infoLayout.addWidget(self.title)
        infoLayout.addStretch()
        infoLayout.addWidget(self.cellCounter)

        bodyLayout.addLayout(infoLayout)
        bodyLayout.addLayout(boardLayout)

        self.setLayout(bodyLayout)

        self.endingWindow = EndingWindow(self)

    def clickedCell(self):
        clicked = self.sender()
        if self.mineSet == False:
            self.mineSet = True
            self.pickedCells = random.sample(list(filter(lambda x: x != clicked, self.cellList)), int(self.bombsAmount))
            for picked in self.cellList:
                if picked in self.pickedCells:
                    picked.mine = True
       
        if not clicked.isClicked:
            clicked.isClicked = True
            self.cellsLeft -= 1
            self.cellCounter.setText(f'Cells Left: {self.cellsLeft}')
            if clicked.mine:
                for cells in self.cellList:
                    if cells.mine:
                        cells.setStyleSheet("background-color: red;")
                        cells.setIcon(QIcon('mine.png'))
                        cells.isMarked = 2
                    else:
                        cells.click()
                self.endingWindow.end.setText('You Lost!')
                self.endingWindow.gameOver()
            else:
                mineCounter = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= clicked.x + i < self.boardSize and 0 <= clicked.y + j < self.boardSize and self.cellList[clicked.x + i + self.boardSize*(clicked.y + j)].mine == True:
                            mineCounter += 1
                if mineCounter == 0:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                                if 0 <= clicked.x + i < self.boardSize and 0 <= clicked.y + j < self.boardSize:
                                    clicked.setStyleSheet("background-color: darkgreen")
                                    self.cellList[clicked.x + i + self.boardSize*(clicked.y + j)].click()
                else:
                    clicked.setStyleSheet("background-color: green; font-size: 20px")
                    clicked.setText(f'{mineCounter}')
            if self.cellsLeft == 0:
                self.endingWindow.end.setText('You Won!')
                self.endingWindow.gameOver()
                
    def rightClick(self):
        clicked = self.sender()
        if not clicked.isMarked and self.bombsLeft > 0 and not clicked.isClicked:
            if clicked.mine:
                self.bombsAmount -= 1
            clicked.isMarked = True
            clicked.setStyleSheet("background-color: red")
            clicked.setIcon(QIcon('flag.png'))
            self.cellsLeft -= 1
            self.cellCounter.setText(f'Cells Left: {self.cellsLeft}')
            self.bombsLeft -= 1
            self.bombCounter.setText(f'Bombs Left: {self.bombsLeft}')
            if self.bombsAmount == 0 and self.cellsLeft == 0:
                self.endingWindow.end.setText('You Won!')
                self.endingWindow.gameOver()
        
        elif clicked.isMarked == 2:
            pass
        
        elif clicked.isMarked and not clicked.isClicked:
            if clicked.mine:
                self.bombsAmount += 1
            clicked.isMarked = False
            clicked.setIcon(QIcon())
            clicked.setStyleSheet("background-color: rgb(29, 26, 161)")
            self.cellsLeft += 1
            self.cellCounter.setText(f'Cells Left: {self.cellsLeft}')
            self.bombsLeft += 1
            self.bombCounter.setText(f'Bombs Left: {self.bombsLeft}')

class EndingWindow(QWidget):
    def __init__(self, prevWindow):
        super().__init__()
        self.setMinimumSize(300,200)
        self.prevWindow = prevWindow
        self.initBody()
    def initBody(self):
        text = QHBoxLayout()
        mainText = QVBoxLayout()
        
        self.end = QLabel('Game Over!'); self.end.setStyleSheet('font-size: 30px')
        self.again = QPushButton('Play Again'); self.again.setStyleSheet('font-size: 30px')
        self.again.clicked.connect(self.playAgain)
        
        text.addStretch()
        text.addWidget(self.end)
        text.addStretch()
        
        mainText.addStretch()
        mainText.addLayout(text)
        mainText.addWidget(self.again)
        mainText.addStretch()

        self.setLayout(mainText)

    def gameOver(self):
        self.show() 
    
    def playAgain(self):
        win.setCurrentIndex(win.currentIndex() - 1)
        win.removeWidget(self.prevWindow)
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(20, 20, 80))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(29, 26, 161))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    win = QStackedWidget()
    sett = SettingsWindow()
    win.addWidget(sett)
    win.setWindowTitle('Minesweeper')
    win.setWindowIcon(QIcon(os.path.join(os.path.abspath('.'), 'logo.ico')))
    win.show()

    sys.exit(app.exec_())