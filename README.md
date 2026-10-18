# TanyaGrafik

Prototipe chatbot **Chart Question Answering** berbahasa
Indonesia untuk membantu pengguna memperoleh informasi dari grafik pada
publikasi statistik, khususnya publikasi statistik BPS Kabupaten
Buleleng.

## Identitas Proyek

  --------------------------------------------------------------------------
  Informasi                           Keterangan
  ----------------------------------- --------------------------------------
  Nama aplikasi                       TanyaGrafik

  Jenis proyek                        Prototipe chatbot Chart Question
                                      Answering
                                      
  Model dasar                         `mPLUG/TinyChart-3B-768`
  
  Vision tower                        `mPLUG/TinyChart-3B-768-siglip`
  
  Model hasil fine-tuning             `https://huggingface.co/shiinn97/tinychart3B-indochartqa`
  
  Dataset                             `https://huggingface.co/datasets/shiinn97/indochartqav2`
  
  Framework backend                   FastAPI
  
  Bahasa antarmuka/pertanyaan         Bahasa Indonesia
  
  Pengembang/peneliti                 Putu Dian Shinta Prativi
  
  Konteks pengembangan                Skripsi, Program Studi
                                      Komputasi Statistik, Politeknik
                                      Statistika STIS
  --------------------------------------------------------------------------

> TanyaGrafik merupakan prototipe penelitian. Jawaban yang dihasilkan
> model perlu diperiksa kembali terhadap grafik dan publikasi statistik
> sumber.

## Deskripsi

TanyaGrafik memungkinkan pengguna mengunggah gambar grafik, menuliskan
pertanyaan terkait grafik tersebut, lalu menerima jawaban dari model
TinyChart yang telah di-*fine-tune* menggunakan dataset IndoChartQA.
Sistem dirancang untuk pertanyaan tertutup yang jawabannya dapat
diperoleh dari informasi visual pada grafik.

Alur umum aplikasi:

1.  Pengguna memilih atau mengunggah gambar grafik.
2.  Pengguna memasukkan pertanyaan dalam bahasa Indonesia.
3.  Antarmuka mengirim gambar dan pertanyaan ke endpoint backend.
4.  Backend menjalankan inferensi model dan mengembalikan jawaban.
5.  Jawaban ditampilkan kepada pengguna

## Teknologi

-   **Python** sebagai bahasa yang digunakan untuk fine-tuning, preprocessing, dan inferensi.
-   **FastAPI** untuk menyediakan backend aplikasi.
-   **TinyChart-3B** sebagai model dasar ChartQA.
-   **LoRA** untuk penyesuaian model (*fine-tuning*).
-   **HTML, CSS, JavaScript, dan Bootstrap 5** untuk antarmuka web.

## Struktur File

tinychart-indochartqa/
``` text
OPENAI.ipynb                # Skrip question-answer generation
Preprocessing.ipynb         # Skrip preprocessing
inference-tinychart.ipynb   # Skrip trial inferensi dan evaluasi
tanyagrafik.ipynb           # Skrip prototipe chatbot TanyaGrafik
tinychart-indochartqa/
├── tinychart/
│   ├── train/
│   │   └── train.py        # Skrip pelatihan
│   └── data/
│       └── dataset.py      # Pengolahan dataset
├── scripts/
│   ├── train_runpod.sh     # Skrip pelatihan
│   ├── convert_model_config.py
│   └── evaluate.sh         # Skrip evaluasi
│   finetuning.ipynb        # Proses keseluruhan fine-tuning
```

## Endpoint Aplikasi

  -----------------------------------------------------------------------
  Endpoint                            Fungsi
  ----------------------------------- -----------------------------------
  `/`                                 Menampilkan halaman utama aplikasi.

  `/predict`                          Menerima gambar grafik dan
                                      pertanyaan, lalu mengembalikan
                                      jawaban model.
  -----------------------------------------------------------------------

Endpoint `/predict` digunakan oleh antarmuka untuk mengirim gambar dan
pertanyaan ke backend. Format input dan respons mengikuti implementasi
pada `app.py`.

## Cara Menjalankan

Langkah berikut merupakan gambaran umum. Sesuaikan perintah instalasi
dan lokasi model dengan konfigurasi proyek yang tersedia.

1.  Siapkan lingkungan Python yang sesuai dengan dependensi model.

2.  Instal dependensi yang tercantum pada berkas `requirements.txt`,
    jika tersedia.

3.  Pastikan model hasil fine-tuning dapat diakses oleh konfigurasi
    inferensi.

4.  Jalankan aplikasi FastAPI sesuai konfigurasi proyek, misalnya:

    ``` bash
    uvicorn app:app --host 0.0.0.0 --port 8000
    ```

5.  Buka alamat lokal yang ditampilkan oleh server pada peramban.

6.  Unggah gambar grafik, tuliskan pertanyaan, lalu kirim untuk
    memperoleh jawaban.

Perintah di atas adalah contoh umum untuk aplikasi FastAPI dengan objek
aplikasi bernama `app` pada `app.py`. Jika nama objek atau konfigurasi
aktual berbeda, sesuaikan perintahnya.

## Batasan

-   Sistem berfokus pada pertanyaan tertutup yang jawabannya dapat
    diturunkan dari grafik.
-   Jawaban dapat keliru jika gambar buram, label tidak terbaca, grafik
    kompleks, atau informasi yang diperlukan tidak ditampilkan.
-   Hasil perhitungan dan interpretasi statistik perlu diverifikasi,
    terutama untuk operasi pada nilai persentase.
-   TanyaGrafik tidak menggantikan publikasi statistik atau sumber data
    resmi.

## Repositori

Repositori kode sumber aplikasi yang pernah digunakan dalam
pengembangan:

Model hasil fine-tuning yang digunakan:

-   Dataset:
    [`shiinn97/indochartqav2`](https://huggingface.co/datasets/shiinn97/indochartqav2)

-   Model:
    [`shiinn97/tinychart3B-indochartqa`](https://huggingface.co/shiinn97/tinychart3B-indochartqa)

------------------------------------------------------------------------
