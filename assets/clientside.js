// assets/clientside.js

// Eğer window.dash_clientside henüz tanımlanmamışsa, boş bir obje olarak başlat
window.dash_clientside = window.dash_clientside || {};

// 'clientside' namespace'i altında fonksiyonlarımızı tanımlıyoruz
window.dash_clientside.clientside = {
    update_theme: function(is_light_on, stored_theme_preference) {
        // Bu fonksiyon, tema switch'inin durumuna göre body'e class ekler/kaldırır
        // ve dcc.Store'a yeni tema tercihini yazar.

        // console.log("Clientside update_theme called. Light mode switch is: " + is_light_on); // Debug için

        let new_theme_preference = 'dark'; // Varsayılan karanlık mod

        if (is_light_on) { // Eğer switch True ise (Aydınlık mod seçili)
            document.body.classList.add('theme-light');
            document.body.classList.remove('theme-dark');
            new_theme_preference = 'light';
        } else { // Eğer switch False ise (Karanlık mod seçili)
            document.body.classList.add('theme-dark');
            document.body.classList.remove('theme-light');
            new_theme_preference = 'dark';
        }

        // dcc.Store'u güncellemek için yeni tema tercihini döndür.
        // Bu, Python tarafında başka callback'lerin bu tercihi kullanabilmesi için
        // veya sayfa yenilendiğinde temanın korunması için faydalı olabilir.
        // (app.py'deki Output('theme-preference-store', 'data') bunu bekliyor)
        return new_theme_preference;
    }
};