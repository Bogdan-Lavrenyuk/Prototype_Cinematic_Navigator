import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, \
    QLineEdit, QListWidget, QListWidgetItem, QFileDialog
from PyQt5.QtGui import QPixmap
from pymongo import MongoClient


class AddMovieWindow(QWidget):
    def __init__(self, update_movie_list_callback):
        super().__init__()
        self.update_movie_list_callback = update_movie_list_callback
        self.setWindowTitle("Додати фільм")

        self.name_label = QLabel("Назва:")
        self.name_input = QLineEdit()

        self.rating_label = QLabel("Оцінка:")
        self.rating_input = QLineEdit()

        self.tagline_label = QLabel("Слоган:")
        self.tagline_input = QLineEdit()

        self.release_date_label = QLabel("Дата виходу:")
        self.release_date_input = QLineEdit()

        self.country_label = QLabel("Країна:")
        self.country_input = QLineEdit()

        self.director_label = QLabel("Режисер:")
        self.director_input = QLineEdit()

        self.genres_label = QLabel("Жанри:")
        self.genres_input = QLineEdit()

        self.actors_label = QLabel("Актори:")
        self.actors_input = QLineEdit()

        self.image_label = QLabel("Фото:")
        self.image_path_input = QLineEdit()
        self.image_button = QPushButton("Оберіть файл")
        self.image_button.clicked.connect(self.select_image)

        self.submit_button = QPushButton("Додати фільм")
        self.submit_button.clicked.connect(self.add_movie)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.rating_label)
        layout.addWidget(self.rating_input)
        layout.addWidget(self.tagline_label)
        layout.addWidget(self.tagline_input)
        layout.addWidget(self.release_date_label)
        layout.addWidget(self.release_date_input)
        layout.addWidget(self.country_label)
        layout.addWidget(self.country_input)
        layout.addWidget(self.director_label)
        layout.addWidget(self.director_input)
        layout.addWidget(self.genres_label)
        layout.addWidget(self.genres_input)
        layout.addWidget(self.actors_label)
        layout.addWidget(self.actors_input)
        layout.addWidget(self.image_label)
        layout.addWidget(self.image_path_input)
        layout.addWidget(self.image_button)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def select_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, "Оберіть фото", "", "Images (*.png *.jpg *.jpeg)")
        if image_path:
            self.image_path_input.setText(image_path)

    def add_movie(self):
        name = self.name_input.text()
        rating = self.rating_input.text()
        tagline = self.tagline_input.text()
        release_date = self.release_date_input.text()
        country = self.country_input.text()
        director = self.director_input.text()
        genres = self.genres_input.text()
        actors = self.actors_input.text()
        image_path = self.image_path_input.text()

        # Збереження фільму у базу даних MongoDB
        client = MongoClient('localhost', 27017)
        db = client['movie_database']
        collection = db['movies']

        movie = {
            "name": name,
            "rating": rating,
            "tagline": tagline,
            "release_date": release_date,
            "country": country,
            "director": director,
            "genres": genres.split(", "),
            "actors": actors.split(", "),
            "image_path": image_path
        }

        collection.insert_one(movie)
        client.close()
        self.update_movie_list_callback()
        self.close()


class MovieDetailsWindow(QWidget):
    def __init__(self, movie):
        super().__init__()
        self.setWindowTitle("Деталі фільму")
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Назва: {movie['name']}"))
        layout.addWidget(QLabel(f"Оцінка: {movie['rating']}"))
        layout.addWidget(QLabel(f"Слоган: {movie['tagline']}"))
        layout.addWidget(QLabel(f"Дата виходу: {movie['release_date']}"))
        layout.addWidget(QLabel(f"Країна: {movie['country']}"))
        layout.addWidget(QLabel(f"Режисер: {movie['director']}"))
        layout.addWidget(QLabel(f"Жанри: {', '.join(movie['genres'])}"))
        layout.addWidget(QLabel(f"Актори: {', '.join(movie['actors'])}"))

        if movie.get('image_path'):
            pixmap = QPixmap(movie['image_path'])
            pixmap = pixmap.scaled(600, 600, aspectRatioMode=True)  # Обмеження розміру зображення
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            layout.addWidget(image_label)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кінематографічний навігатор")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.add_movie_button = QPushButton("Додати фільм")
        self.add_movie_button.clicked.connect(self.open_add_movie_window)

        self.movie_list = QListWidget()
        self.movie_list.itemDoubleClicked.connect(self.show_movie_details)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введіть ключові слова")

        self.search_button = QPushButton("Пошук")
        self.search_button.clicked.connect(self.search_movies)

        self.clear_button = QPushButton("Очистити")
        self.clear_button.clicked.connect(self.clear_search)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_button)  # Додаємо кнопку "Очистити" у макет

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.add_movie_button)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.movie_list)

        self.central_widget.setLayout(main_layout)

        self.update_movie_list()

    def open_add_movie_window(self):
        self.add_movie_window = AddMovieWindow(self.update_movie_list)
        self.add_movie_window.show()

    def update_movie_list(self):
        self.movie_list.clear()
        client = MongoClient('localhost', 27017)
        db = client['movie_database']
        collection = db['movies']
        movies = collection.find()

        for movie in movies:
            item = QListWidgetItem(movie['name'])
            item.setData(1000, movie)  # Custom data storage
            self.movie_list.addItem(item)

        client.close()

    def search_movies(self):
        keywords = self.search_input.text().split()
        self.movie_list.clear()
        client = MongoClient('localhost', 27017)
        db = client['movie_database']
        collection = db['movies']

        query = {"$and": []}
        for keyword in keywords:
            query["$and"].append({
                "$or": [
                    {"name": {"$regex": keyword, "$options": "i"}},
                    {"rating": {"$regex": keyword, "$options": "i"}},
                    {"tagline": {"$regex": keyword, "$options": "i"}},
                    {"release_date": {"$regex": keyword, "$options": "i"}},
                    {"country": {"$regex": keyword, "$options": "i"}},
                    {"director": {"$regex": keyword, "$options": "i"}},
                    {"genres": {"$regex": keyword, "$options": "i"}},
                    {"actors": {"$regex": keyword, "$options": "i"}}
                ]
            })

        movies = collection.find(query)

        for movie in movies:
            item = QListWidgetItem(movie['name'])
            item.setData(1000, movie)  # Custom data storage
            self.movie_list.addItem(item)

        client.close()

    def clear_search(self):
        self.search_input.clear()
        self.update_movie_list()

    def show_movie_details(self, item):
        movie = item.data(1000)
        self.movie_details_window = MovieDetailsWindow(movie)
        self.movie_details_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())