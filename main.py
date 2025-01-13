import sys # Veri argümanlarına erişmke için kuulanılır 
import sqlite3 # Veri Tabanı 
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QStackedWidget
) # Arayüzü Oluşturmak için gerekli widgetler 
from PyQt5.QtCore import Qt # Temel ÖZellikler için 
import math 

DB_NAME = "carpets.db" # halı bilgilerini barındıran veri tabanının adı 
# SINIF TANIMI VE KURULUM 
class FocusableLineEdit(QLineEdit): # kullanıcıdan metin girişi almayı sağlayan bir sınıf türüdür.
    def __init__(self, next_widget=None): # __init__ sınıfın kurucusudur 
        super().__init__() # Class da var olan özellikelrinin çağrılmsını sağlar
        self.next_widget = next_widget # enter tuşuna veya return tuşuna basıldıpında bir sonraki widget a geçemyi temsil eder

    def keyPressEvent(self, event): # hangi tuşa basıldıpını anlamak için kullanılır. (Enter ve return tuşu)
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.next_widget: 
                self.next_widget.setFocus()
        else:# tuş normal işlevine devam etmesi sağlanır
            super().keyPressEvent(event)# sınıf metodu çağrılı ve işlem kaldığı yerden devam eder

class CarpetManagementWidget(QWidget): # uygulama widgetleri için özel bi sınıf olutşurduğunu gösterir
    def __init__(self, parent=None):  
        super().__init__(parent) # qwidget çağrılarak temel özellikleri yükler
        self.layout = QVBoxLayout()# dikey düzen 
        self.setLayout(self.layout)#ana vidgete dikey düzeni uygular

        #VERİTABANI BAŞLATMA 
        self.init_db()# veri tabanı kontrol edilir veya oluşturulur

        # GİRİŞ BİLGİLERİ VE YERLEŞİMİ AYARLAMA 
        self.input_layout = QVBoxLayout()
        self.layout.addLayout(self.input_layout)# yeni dikey düzen oluşturur ana düzene ekler

        field_names = ['BARKOD', 'KALITE', 'DESEN', 'EN(CM)', 'BOY(CM)', 'RENK', 'ADET', 'TUR']
        self.fields = {}# gerekli olan bilgilerin adlarını tutar; alanların referansını tutan bir sözlüktür
        
        for name in field_names: 
            self.fields[name] = FocusableLineEdit() # metin bilgisi alınır ve self. files içinde saklanır

        for i in range(len(field_names) - 1): 
            self.fields[field_names[i]].next_widget = self.fields[field_names[i + 1]]
        # enter tuşuna basıldığında bir sonraki alana odaklanmayı sağlar
        for label_text, line_edit in self.fields.items():
            row_layout = QHBoxLayout() # yatay düzen 
            label = QLabel(label_text + ":")# etiket ve metin kutusu bu düzenin içine eklenir
            row_layout.addWidget(label)
            row_layout.addWidget(line_edit)
            self.input_layout.addLayout(row_layout) # tüm satırlar içine birer birer eklenir
       # DÜĞMELERİ AYARLAMA
        button_layout = QHBoxLayout()# Tekrar yatay bir düzen oluşturur 
        self.btn_add = QPushButton("HALI EKLE")
        self.btn_view = QPushButton("HALILARI GOSTER")
        self.btn_delete = QPushButton("SECILENLERI SIL")# yapıalcak işlemler için buton tanımlanır
        button_layout.addWidget(self.btn_add)#düğmeler yatay düzleme eklenir ve
        button_layout.addWidget(self.btn_view) 
        button_layout.addWidget(self.btn_delete)
        self.layout.addLayout(button_layout) # ana düzenin içine eklenir.

        self.fields[field_names[-1]].next_widget = self.btn_add

        self.btn_add.clicked.connect(self.add_record)
        self.btn_view.clicked.connect(self.toggle_table_view)
        self.btn_delete.clicked.connect(self.delete_selected_records)

        self.btn_add.setFocusPolicy(Qt.StrongFocus)
        self.btn_add.keyPressEvent = self.button_key_press_event
        # TABLOYU AYARLAMA 
        self.table = QTableWidget()# Tablo oluşturur
        self.table.setColumnCount(9)# Atanacak sütun sayısı belirlenir
        self.table.setHorizontalHeaderLabels([
            'BARKOD', 'KALITE', 'DESEN', 'EN(CM)', 'BOY(CM)',
            'RENK', 'ADET', 'TUR', 'EBAT (M2)'
        ])# Atanacak sütunların ismi girilir
        
        self.table.setSelectionMode(QTableWidget.MultiSelection)# birden fazla satır seçmeyi sağlar
        self.table.setSelectionBehavior(QTableWidget.SelectRows)# seçim davranışı, tüm satırın seçilmesini sağlar
        self.layout.addWidget(self.table)
        
        self.table.hide()# başlangıçta tablo gizlzenir
        self.btn_delete.hide()# başlangıçta sil butonu gizlenir
        
        self.table_visible = False
        self.record_ids = []
        

    def init_db(self):# veritabanı içerisine halı bilgilerini içeren tablo tanımlanır
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS carpets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barkod TEXT,
                kalite TEXT,
                desen TEXT,
                en_cm TEXT,
                boy_cm TEXT,
                renk TEXT,
                adet TEXT,
                tur TEXT,
                ebat_m2 TEXT
            )
        """)
        conn.commit()
        conn.close()

    def toggle_table_view(self): # tablo görünürlüğünü değiştirir. 
        if not self.table_visible:
            self.view_records()
            self.table.show()
            self.btn_delete.show()
            self.btn_view.setText("HALILARI GIZLE")
        else:
            self.table.hide()
            self.btn_delete.hide()
            self.btn_view.setText("HALILARI GOSTER")
        
        self.table_visible = not self.table_visible

    def delete_selected_records(self):#seçilen satıralrı veri tabanından siler
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "UYARI", "LUTFEN SILINECEK KAYITLARI SECIN.")
            return

        reply = QMessageBox.question(self, 'SILME ONAYI',
                                   f'{len(selected_rows)} KAYDI SILMEK ISTEDIGINIZDEN EMIN MISINIZ?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                
                deleted_count = 0
                for row in sorted(selected_rows, reverse=True):
                    if 0 <= row < len(self.record_ids):
                        record_id = self.record_ids[row]
                        cur.execute("DELETE FROM carpets WHERE id = ?", (record_id,))
                        deleted_count += 1

                conn.commit()
                conn.close()

                QMessageBox.information(self, "BASARILI", f"{deleted_count} KAYIT BASARIYLA SILINDI!")
                self.view_records()
            except Exception as e:
                QMessageBox.critical(self, "HATA", f"KAYITLAR SILINEMEDI:\n{e}")

    def button_key_press_event(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.add_record()
            self.fields['BARKOD'].setFocus()

    def add_record(self): # veri tabanına yeni bir kayıt eklenir eğer aynı halıysa adet artırılır
        barkod = self.fields['BARKOD'].text().strip()
        kalite = self.fields['KALITE'].text().strip()
        desen = self.fields['DESEN'].text().strip()
        en_cm = self.fields['EN(CM)'].text().strip()
        boy_cm = self.fields['BOY(CM)'].text().strip()
        renk = self.fields['RENK'].text().strip()
        adet = self.fields['ADET'].text().strip()
        tur = self.fields['TUR'].text().strip()

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, adet FROM carpets 
            WHERE barkod=? AND kalite=? AND desen=? AND en_cm=? 
            AND boy_cm=? AND renk=? AND tur=?
        """, (barkod, kalite, desen, en_cm, boy_cm, renk, tur))
        
        existing_carpet = cur.fetchone()

        try:
            if existing_carpet:
                carpet_id = existing_carpet[0]
                current_adet = int(existing_carpet[1])
                new_adet = current_adet + int(adet)
                
                cur.execute("""
                    UPDATE carpets 
                    SET adet=? 
                    WHERE id=?
                """, (str(new_adet), carpet_id))
                
                QMessageBox.information(self, "BASARILI", "HALI ADEDI BASARIYLA GUNCELLENDI!")
            else:
                try:
                    en_float = float(en_cm)
                    boy_float = float(boy_cm)
                    adet_float = float(adet)
                    ebat_m2 = math.ceil((en_float * boy_float * adet_float) / 10000.0)
                except ValueError:
                    ebat_m2 = 0.0

                cur.execute("""
                    INSERT INTO carpets (
                        barkod, kalite, desen, en_cm, boy_cm, renk, adet, tur, ebat_m2
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    barkod, kalite, desen,
                    en_cm, boy_cm, renk,
                    adet, tur, str(ebat_m2)
                ))
                
                QMessageBox.information(self, "BASARILI", "YENI HALI KAYDI BASARIYLA EKLENDI!")

            conn.commit()

            for field in self.fields.values():
                field.clear()

            self.fields['BARKOD'].setFocus()

            if self.table_visible:
                self.view_records()

        except Exception as e:
            QMessageBox.critical(self, "HATA", f"KAYIT ISLEMI BASARISIZ:\n{e}")
        finally:
            conn.close()

    def view_records(self): # veri tabanındaki tüm kayıtlar tabloya eklenir.
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, barkod, kalite, desen, en_cm, boy_cm, renk, adet, tur, ebat_m2
            FROM carpets
        """)
        records = cur.fetchall()
        conn.close()

        self.record_ids = [record[0] for record in records]
        self.table.setRowCount(len(records))
        
        for row_index, row_data in enumerate(records):
            for col_index, col_data in enumerate(row_data[1:]):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_index, col_index, item)

class MainPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)# Metod ebeveyn kodu çağırır
        layout = QVBoxLayout()# dikey düzenleme alanıdır
        self.setLayout(layout)# düzenleme alanını pencerenin genel düzeni olarak ayrlar

        title = QLabel("HALI STOK UYGULAMASI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)# etileti düzenleme alanına ekler

        
        self.search_layout = QHBoxLayout()# bileşenler yatay olarak hizalanır 
        
        self.lbl_search = QLabel("BARKOD:")# arama için açıklama etiketi label etiket demek 
        self.search_lineedit = QLineEdit()# arma için metin girişi kısmı 
        self.btn_search = QPushButton("ARA")# aramayı gerçekleştirir
        
        self.search_layout.addWidget(self.lbl_search)# çıktıları yatay düzleme sıralar 
        self.search_layout.addWidget(self.search_lineedit)
        self.search_layout.addWidget(self.btn_search)
        
        layout.addLayout(self.search_layout)

        # Tablo oluşturur
        self.search_table = QTableWidget()
        self.search_table.setColumnCount(9)
        self.search_table.setHorizontalHeaderLabels([
            'BARKOD', 'KALITE', 'DESEN', 'EN(CM)', 'BOY(CM)',
            'RENK', 'ADET', 'TUR', 'EBAT (M2)'
        ])

        

        
        self.search_table.setSelectionMode(QTableWidget.NoSelection)# tablo hücresi seçimini engeller 
        self.search_table.setSelectionBehavior(QTableWidget.SelectRows)# sütun seçmeyi sağlar 
        self.search_table.hide()# başlangıçta tabloyu gizler  
        layout.addWidget(self.search_table)# tablo dike düzenleme alanına eklenir
        
       
        self.btn_search.clicked.connect(self.search_carpet)

        layout.addSpacing(5)# düzenleme alanına 5 piksel boşluk koyar

        
        button_container = QVBoxLayout()# dikey düzen oluşturur
        button_container.setSpacing(20)#arasına 20 piksel boşluk koyar

        
        self.btn_carpet_management = QPushButton("HALI YONETIMI")
        self.btn_carpet_management.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 15px; 
                min-width: 100px;
            }
        """)# font boyutunu, iç boşluğunu, minimum genişliğini 
        button_container.addWidget(self.btn_carpet_management, alignment=Qt.AlignCenter)

        layout.addLayout(button_container)
        self.btn_carpet_management.setFixedSize(200, 50) 

    def search_carpet(self):# barkod arama işlevini gerçekleşiren yer
        from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem# uyarı mesajı ve tablo ögesini içeri aktarmak için kullanılır 

        barkod_search = self.search_lineedit.text().strip()# barkod değerini işler 
        if not barkod_search:
            QMessageBox.warning(self, "Uyarı", "Lütfen arama için barkod giriniz!")
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()# imleç oluturur
        cur.execute("""
            SELECT barkod, kalite, desen, en_cm, boy_cm, renk, adet, tur, ebat_m2
            FROM carpets
            WHERE barkod LIKE ?
        """, ('%' + barkod_search + '%',))# eşleşen kayıtları arar 
        results = cur.fetchall()#tüm sonuçarlı bir liste olarak alır
        conn.close()# ver itabanı balantısnı kpatır

        if not results:
            self.search_table.hide()
            QMessageBox.information(self, "Bilgi", "Aranan barkoda ait sonuç bulunamadı.")
            return

       
        self.search_table.setRowCount(len(results))# sonuç sayısı kadar satır ekler 
        self.search_table.show()# tabloyu görünür yapar

        for row_index, row_data in enumerate(results):# sonuçalrın her satırını dolaşır 
            for col_index, col_value in enumerate(row_data):# satırdaki her hücre değerini işler
                item = QTableWidgetItem(str(col_value))# bir öge oluşturur
                
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)# hücreleri sadece okunabilir yapar 
                self.search_table.setItem(row_index, col_index, item)# hücre ögesini tabloya ekler 

class MainWindow(QMainWindow):#uygulamanın ana görnümünü barındıran sınıftır 
    def __init__(self):# sınıfın kurucusudur
        super().__init__()
        self.setWindowTitle("HALI MAGAZASI UYGULAMASI")
        self.setGeometry(550, 300, 800, 600)# x, y 

        
        self.stacked_widget = QStackedWidget()#sayfalar arası geçiş yapmayı sağlar
        self.setCentralWidget(self.stacked_widget)

        self.main_page = MainPage()# ana sayfayı oluşturur
        self.carpet_management = CarpetManagementWidget()# 2. sayafayı oluşturur

        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.carpet_management)

        
        self.main_page.btn_carpet_management.clicked.connect(self.show_carpet_management)
        # ana sayada halı yönetimi butonunu çalıştırır
        back_button = QPushButton("ANA SAYFA")# düğme 
        self.carpet_management.layout.insertWidget(0, back_button)
        back_button.clicked.connect(self.show_main_page)

    def show_main_page(self):
        self.stacked_widget.setCurrentWidget(self.main_page)# ana sayfaya döndürür

    def show_carpet_management(self):
        self.stacked_widget.setCurrentWidget(self.carpet_management)# halı ynöetim sayfasına yönledirir

def main():#uygulama başlangıçı
    app = QApplication(sys.argv)# PyQt uygulamasını başlatır ve komut satırlarını kabul eder 
    window = MainWindow()# uygulama için bir pencere oluşturur
    window.show()# pencereyi görnünr hale getirir
    sys.exit(app.exec_())# uygulama penceresini sorunsuz kapatmayı sağlar.

if __name__ == "__main__":
    main()# modül doğrudan çağrıldığında uygulama başlar . 
