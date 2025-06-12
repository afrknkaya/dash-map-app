# components/data_loader.py
import pandas as pd
import os

# --- CSV DOSYA ADLARI ---
COUNTRY_FILE_NAME = 'Country.csv'
# --- CSV DOSYA ADLARI (SON) ---

# --- CSV DOSYASINDAKİ GERÇEK SÜTUN ADLARI (Country.csv için) ---
SUTUN_CSV_ULKE = 'Country'
SUTUN_CSV_TEKNOLOJI = 'Technology'
SUTUN_CSV_YIL = 'Year'
SUTUN_CSV_DEGER_KAPASITE = 'Electricity Installed Capacity (MW)'
SUTUN_CSV_ISO_CODE = 'ISO3 code' # <-- HARİTA İÇİN YENİ EKLENDİ
# --- CSV SÜTUN ADLARI (SON) ---

# --- DİĞER MODÜLLER TARAFINDAN KULLANILACAK STANDART SÜTUN ADI DEĞİŞKENLERİ ---
SUTUN_ULKE = SUTUN_CSV_ULKE
SUTUN_TEKNOLOJI = SUTUN_CSV_TEKNOLOJI
SUTUN_YIL = SUTUN_CSV_YIL
SUTUN_DEGER = SUTUN_CSV_DEGER_KAPASITE
SUTUN_ISO_CODE = SUTUN_CSV_ISO_CODE # <-- HARİTA İÇİN YENİ EKLENDİ

# Metrik ve Birim Bilgileri (Country.csv'deki değer sütunundan türetilmiş)
SUTUN_BIRIM_DEGERI = 'MW'
SUTUN_METRIK_ADI = 'Üretim Kapasitesi'
# --- STANDART SÜTUN ADI DEĞİŞKENLERİ (SON) ---

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data')
COUNTRY_FILE_PATH = os.path.join(DATA_PATH, COUNTRY_FILE_NAME)

def load_and_prepare_country_data():
    """
    Ülke kapasite verilerini (Country.csv) yükler, temel temizlik ve ön hazırlık yapar.
    Dönüş değerleri: DataFrame, filters_data (dict), metrics_info (dict)
    """
    try:
        df = pd.read_csv(COUNTRY_FILE_PATH)
        # print(f"data_loader.py: '{COUNTRY_FILE_NAME}' okundu. {len(df)} satır.")
        # print(f"data_loader.py: CSV'deki Orijinal Sütunlar: {df.columns.tolist()}")

        required_csv_cols = [
            SUTUN_CSV_ULKE, 
            SUTUN_CSV_TEKNOLOJI, 
            SUTUN_CSV_YIL, 
            SUTUN_CSV_DEGER_KAPASITE,
            SUTUN_CSV_ISO_CODE # <-- GEREKLİ SÜTUNLARA EKLENDİ
        ]
        missing_csv_cols = [col for col in required_csv_cols if col not in df.columns]
        if missing_csv_cols:
            print(f"HATA (data_loader.py): '{COUNTRY_FILE_NAME}' dosyasında şu temel sütunlar bulunamadı: {missing_csv_cols}")
            return pd.DataFrame(), {}, {}
        
        if df[SUTUN_CSV_DEGER_KAPASITE].dtype == 'object':
            df[SUTUN_CSV_DEGER_KAPASITE] = df[SUTUN_CSV_DEGER_KAPASITE].astype(str).str.replace(',', '', regex=False)
        df[SUTUN_CSV_DEGER_KAPASITE] = pd.to_numeric(df[SUTUN_CSV_DEGER_KAPASITE], errors='coerce')
        df[SUTUN_CSV_YIL] = pd.to_numeric(df[SUTUN_CSV_YIL], errors='coerce').astype('Int64')

        # ISO Kodu olmayan veya temel değerleri eksik olan satırları temizle
        df.dropna(subset=[
            SUTUN_YIL, SUTUN_DEGER, SUTUN_ULKE, SUTUN_TEKNOLOJI, SUTUN_ISO_CODE # <-- DROPNA'YA EKLENDİ
        ], inplace=True)

        if df.empty:
            # print(f"UYARI (data_loader.py): '{COUNTRY_FILE_NAME}' için eksik değerler temizlendikten sonra hiç veri kalmadı!")
            return pd.DataFrame(), {}, {}

        unique_years = sorted(df[SUTUN_YIL].unique().astype(int)) # int'e çevirdik
        unique_countries = sorted(df[SUTUN_ULKE].unique())
        unique_technologies = sorted(df[SUTUN_TEKNOLOJI].unique())
        
        filters_data = {
            'years': unique_years,
            'countries': unique_countries,
            'technologies': unique_technologies
        }
        metrics_info = {
            'ana_metrik': {
                'isim': SUTUN_METRIK_ADI,
                'deger_sutunu': SUTUN_DEGER,
                'birim': SUTUN_BIRIM_DEGERI
            }
        }
        
        # print(f"data_loader.py: '{COUNTRY_FILE_NAME}' için veri yükleme ve ön hazırlık tamamlandı.")
        return df, filters_data, metrics_info
    except FileNotFoundError:
        print(f"HATA (data_loader.py): {COUNTRY_FILE_PATH} dosyası bulunamadı.")
        return pd.DataFrame(), {}, {}
    except Exception as e:
        print(f"HATA (data_loader.py): '{COUNTRY_FILE_NAME}' verisi yüklenirken bir hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame(), {}, {}

if __name__ == '__main__':
    print("--- data_loader.py doğrudan çalıştırılıyor (Test Modu) ---")
    df_country_test, filters_test, metrics_info_test = load_and_prepare_country_data()
    if not df_country_test.empty:
        print("\nTest: Ülke Veri Başlığı (ilk 3 satır) - Kullanılacak Sütunlar:")
        # Test için SUTUN_ISO_CODE'u da ekleyelim
        display_cols_test = [SUTUN_ULKE, SUTUN_ISO_CODE, SUTUN_TEKNOLOJI, SUTUN_YIL, SUTUN_DEGER]
        # Sadece var olan sütunları gösterelim
        display_cols_test_existing = [col for col in display_cols_test if col in df_country_test.columns]
        print(df_country_test[display_cols_test_existing].head(3))
        
        print(f"\nTest: Veri Tipleri (Yıl, Değer):\n{df_country_test[[SUTUN_YIL, SUTUN_DEGER]].dtypes}")
        if SUTUN_ISO_CODE in df_country_test.columns:
             print(f"Test: ISO Kodu Sütun Tipi: {df_country_test[SUTUN_ISO_CODE].dtype}")
        print("\nTest: Filtreler için Hazırlanan Veri:")
        for key_test, val_test in filters_test.items():
            print(f"- {key_test.capitalize()} (sayısı: {len(val_test)}, ilk 3): {val_test[:3] if len(val_test) > 0 else 'Yok'}")
        print("\nTest: Metrik Bilgisi (metrics_info):")
        print(metrics_info_test)
    else:
        print(f"Test: Ülke verisi ({COUNTRY_FILE_NAME}) yüklenemedi veya boş.")