# دليل النشر والتشغيل السحابي (CapitalTrain Cloud Deployment)

## 📌 معلومات البنية التحتية
- **الاستضافة السحابية:** Render.com (Service: `capitaltrain`)
- **مستودع الكود:** GitHub (`wmoafi/capitaltrain`, branch: `main`)
- **الدومين الخارجي:** `https://capitaltrain.tafawuq-edu.site`
- **التشغيل:** سحابي بالكامل عبر `run_service.py` (تشغيل الويب + بوت التليجرام سحابياً).
- **لا توجد أنفاق محلية:** تم الاستغناء عن الأنفاق المحلية نهائياً.

## 🚀 دورة التحديث:
1. التعديل في `I:\CapitalTrain\`
2. اختبار سلامة الكود
3. `git add . && git commit -m "..." && git push origin main`
4. رندر يقوم بالنشر التلقائي فوراً.
