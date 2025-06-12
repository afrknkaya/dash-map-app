# components/region_data_loader.py
import pandas as pd
import os

# --- Sabitler ---
REGION_FILE_NAME = 'Region.csv'

# Region.csv'deki Sütun Adları
SUTUN_CSV_BOLGE = 'Region'
SUTUN_CSV_RE_NON_RE = 'RE or Non-RE'
SUTUN_CSV_GRUP_TEKNOLOJI = 'Group Technology'
SUTUN_CSV_YIL = 'Year'
SUTUN_CSV_DEGER = 'Sum of Electricity Installed Capacity (MW)'

# Sayfalarda kullanılacak standart değişken adları (daha anlaşılır olması için)
SUTUN_BOLGE_REG = SUTUN_CSV_BOLGE
SUTUN_RE_NON_RE_REG = SUTUN_CSV_RE_NON_RE
SUTUN_GRUP_TEKNOLOJI_REG = SUTUN_CSV_GRUP_TEKNOLOJI
SUTUN_YIL_REG = SUTUN_CSV_YIL
SUTUN_DEGER_REG = SUTUN_CSV_DEGER

# Metrik Bilgileri
METRIK_ADI_REG = 'Kurulu Kapasite'
METRIK_BIRIM_REG = 'MW'

def load_and_prepare_region_data():
    """
    Region.csv dosyasını yükler, temizler ve bölgesel analiz için hazırlar.

    Dönen Değerler:
    - df_region (DataFrame): İşlenmiş bölgesel veriler.
    - filters (dict): Filtreler için kullanılacak benzersiz değerleri içerir.
    - metrics_info (dict): Metrik adı ve birimi gibi bilgileri içerir.
    """
    try:
        # Dosya yolunu belirle
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'data', REGION_FILE_NAME)
        
        df_region = pd.read_csv(file_path)

        # Gerekli sütunların varlığını kontrol et
        required_cols = [
            SUTUN_CSV_BOLGE, SUTUN_CSV_RE_NON_RE, SUTUN_CSV_GRUP_TEKNOLOJI,
            SUTUN_CSV_YIL, SUTUN_CSV_DEGER
        ]
        missing_cols = [col for col in required_cols if col not in df_region.columns]
        if missing_cols:
            print(f"HATA (region_data_loader): '{REGION_FILE_NAME}' dosyasında sütunlar eksik: {missing_cols}")
            return pd.DataFrame(), {}, {}

        # Veri tiplerini düzelt
        df_region[SUTUN_DEGER_REG] = pd.to_numeric(df_region[SUTUN_DEGER_REG], errors='coerce').fillna(0)
        df_region[SUTUN_YIL_REG] = pd.to_numeric(df_region[SUTUN_YIL_REG], errors='coerce').dropna().astype(int)

        # Eksik verileri temizle
        df_region.dropna(subset=required_cols, inplace=True)
        if df_region.empty:
            print(f"UYARI (region_data_loader): '{REGION_FILE_NAME}' için veri kalmadı.")
            return pd.DataFrame(), {}, {}

        # Filtreler için benzersiz değerleri listele
        unique_regions = sorted(df_region[SUTUN_BOLGE_REG].unique().tolist())
        unique_re_non_re = sorted(df_region[SUTUN_RE_NON_RE_REG].unique().tolist())
        unique_group_techs = sorted(df_region[SUTUN_GRUP_TEKNOLOJI_REG].unique().tolist())
        unique_years = sorted(df_region[SUTUN_YIL_REG].unique().tolist())

        filters_data = {
            'regions': unique_regions,
            're_non_re': unique_re_non_re,
            'group_technologies': unique_group_techs,
            'years': unique_years
        }

        metrics_info = {
            'ana_metrik': {
                'isim': METRIK_ADI_REG,
                'birim': METRIK_BIRIM_REG,
                'deger_sutunu': SUTUN_DEGER_REG
            }
        }
        
        print(f"Bölgesel veri (Region.csv) başarıyla yüklendi. {len(df_region)} satır.")
        return df_region, filters_data, metrics_info

    except FileNotFoundError:
        print(f"HATA: '{REGION_FILE_NAME}' dosyası 'data' klasöründe bulunamadı.")
        return pd.DataFrame(), {}, {}
    except Exception as e:
        print(f"HATA: '{REGION_FILE_NAME}' dosyası işlenirken bir hata oluştu: {e}")
        return pd.DataFrame(), {}, {}

# Bu dosyayı doğrudan çalıştırmak için test bloğu
if __name__ == '__main__':
    df, filters, metrics = load_and_prepare_region_data()
    if not df.empty:
        print("\n--- Bölgesel Veri Yükleyici Testi Başarılı ---")
        print("İlk 5 satır:")
        print(df.head())
        print("\nVeri Tipleri:")
        df.info()
        print("\nFiltreler için Çıkarılan Benzersiz Değerler:")
        for key, val in filters.items():
            print(f"- {key.capitalize()}: (sayısı: {len(val)}) -> {val[:5]}")
        print("\nMetrik Bilgisi:")
        print(metrics)