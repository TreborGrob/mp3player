from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from threading import Timer
from kivy.core.window import Window
import easygui
from mutagen.mp3 import MP3

Window.size = (400, 400)


class PlayerExample(BoxLayout):
    slider = ObjectProperty(None)
    filename = ObjectProperty(None)
    play = ObjectProperty(None)
    pause = ObjectProperty(None)
    stop = ObjectProperty(None)
    time = ObjectProperty(None)
    all_time = ObjectProperty(None)
    sound = None
    timer = None
    music_file = None
    seconds = 0

    def load_music(self):
        # если таймер не равен none то останавливаем таймер
        if self.timer is not None:
            self.timer.cancel()
        # выбираем путь к файлу
        self.music_file = easygui.fileopenbox(filetypes=["*.mp3"])
        if self.sound is not None:
            self.stop_music()
            self.seconds = 0
            self.time.text = '00:00'
        # откл.кнопку плей если нет файла, и присваиваем значения файлнейм и таймеру
        if self.music_file is None:
            self.filename.text = "No loaded song"
            self.all_time.text = '00:00'
            if self.timer is not None:
                self.timer.cancel()
            self.play.disabled = True
            return
        # присваиваем загруженный трек в переменную саунд
        self.sound = SoundLoader.load(self.music_file)
        # инфа о файле
        audio = MP3(self.music_file)
        # переводим размер трека в минуты
        m, s = divmod(audio.info.length + 1, 60)
        # отображение времени в формате "минуты:секунды"
        t = '%02d:%02d' % (m, s)
        # присваиваем переменной алл_тайм значение переменной т
        self.all_time.text = t
        # максимальное значение виджета будет равно длительности загр. трека
        self.slider.max = int(audio.info.length)
        # значение ползунка
        self.slider.value = 0
        # позиция трека с помощью метода seek
        self.sound.seek(0)
        # остановка проигрывания
        self.sound.stop()
        # вкл. кнопку плей
        self.play.disabled = False

        self.timer = Timer(1, self.position)
        self.filename.text = self.sound.source

    def play_music(self):
        self.play.disabled = True
        self.pause.disabled = False
        self.stop.disabled = False
        self.sound.play()
        self.timer.start()

    def pause_music(self):
        self.timer.cancel()
        pos = self.sound.get_pos()
        self.sound.stop()
        self.slider.value = pos
        self.play.disabled = False
        self.pause.disabled = True
        self.timer = Timer(1, self.position)

    def stop_music(self):
        self.sound.stop()
        self.timer.cancel()
        self.play.disabled = False
        self.timer = Timer(1, self.position)
        self.slider.value = 0
        self.sound.seek(0)
        self.stop.disabled = True
        self.pause.disabled = True

    def position(self):
        self.timer = Timer(1, self.position)
        self.slider.value = self.sound.get_pos()
        self.timer.start()
        self.seconds += 1
        self.time_format(self.seconds)
        if self.slider == 0:
            self.stop_music()
            self.slider.value = 0
            self.seconds = 0
            self.time_format(self.seconds)

    def music_position(self, instance):  # instance - объект который вызывает текущий метод (Slider)
        if self.sound is not None:
            self.sound.seek(instance.value)
            self.seconds = instance.value
            self.time_format(self.seconds)

    def time_format(self, seconds):
        m, s = divmod(seconds, 60)
        t = "%02d:%02d" % (m, s)
        self.time.text = t


class PlayerApp(App):
    player = None

    def build(self):
        Window.bind(on_close=self.on_request_close)
        self.player = PlayerExample()
        return self.player

    def on_request_close(self, *args):
        self.player.sound.stop()
        self.player.timer.cancel()


if __name__ == '__main__':
    PlayerApp().run()
