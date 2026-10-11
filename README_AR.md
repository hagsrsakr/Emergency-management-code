# المرحلة الثانية: Real CAD + AI + SHAP + MILP

هذا المشروع هو النسخة البحثية العملية التالية للمشروع السابق. الهدف هو ربط أربعة أجزاء في خط واحد قابل لإعادة التشغيل:

1. **بيانات CAD حقيقية** من مصدر حكومي مفتوح.
2. **AI** لفهم الحالة والتنبؤ بالأولوية التشغيلية وزمن الاستجابة.
3. **SHAP** لتفسير لماذا أعطى النموذج هذا التنبؤ.
4. **MILP** لتخصيص الموارد المتاحة فعليًا، مع استخدام مصفوفة Incident × Resource مبنية من CAD الحقيقي دون اختراع GPS للوحدات.

## ما تم إصلاحه

- لا توجد `resource_locations.csv` مصطنعة.
- لا يعتمد MILP على عمود `priority_numeric` مفقود؛ يتم تطبيع `final_priority` إلى `priority_urgency` من تعريفات المصدر Code 2/Code 3.
- مصفوفة Incident × Resource تبنى من **الحالة الفعلية للتوافر** في CAD ومن **السلوك التاريخي الحقيقي لزمن الاستجابة**.
- التاريخ المستخدم لبناء الـhistorical response matrix هو فترة التدريب فقط عند إنشاء test matrix زمني، لمنع تسرب الهدف، بينما حالة توافر المورد تُستخرج من الـCAD الكامل لأنها تمثل حالة تشغيلية مرصودة عند لحظة القرار.
- يتم فصل **Temporal Holdout** عن **Spatial Holdout**.
- توجد Repeated Cross-Validation داخل مجموعة التدريب كتحقق إضافي، بينما الاختبار الزمني هو الاختبار الأساسي للتعميم المستقبلي.
- SHAP له تفسير Global وLocal.
- المقارنة الإحصائية تستخدم نفس الحوادث بين الاستراتيجيات عند توافر جميع النتائج.
- لا يتم اختراع Traffic data. طبقة المرور اختيارية وتعمل فقط عندما يضاف ملف حقيقي موثق.

## مصدر البيانات الأساسي

San Francisco Fire Department and Emergency Medical Services Dispatched Calls for Service, Dataset ID `nuek-vuh3`.

المصدر هو San Francisco Open Data، وهو مستخرج من Computer-Aided Dispatch، ويضم أزمنة الاستلام والتوجيه والاستجابة والوصول والتوافر، إضافة إلى الأولوية التشغيلية وأنواع الوحدات. المصدر محدث يوميًا. راجع `docs/DATA_PROVENANCE_AR.md`.


## حل خطأ HTTP 403 في تنزيل SF CAD

إذا ظهر: `requests.exceptions.HTTPError: 403 Client Error: Forbidden` فهذا يعني أن خادم Socrata رفض طلب API الحالي. وثائق Socrata الحالية توصي باستخدام **App Token** لطلبات API، وتوضح أن الطلبات غير الموثقة تخضع لقيود وصول/تخفيضات أكبر.

السكربت الجديد `scripts/01_download_sf_cad.py` يعالج ذلك كالتالي:

1. يحاول أولًا CSV endpoint بحجم صفحات صغير (5000 صف).
2. إذا رُفض الطلب، ينتقل تلقائيًا إلى SODA v3 POST query.
3. إذا وُجد المتغير `SF_APP_TOKEN` يرسله في `X-App-Token`.
4. يحفظ الملف دائمًا داخل مجلد المشروع: `data/sf_cad_raw.csv` حتى عند التشغيل من PyCharm/VS Code.

### إعداد App Token في Windows

في CMD:
```bat
set SF_APP_TOKEN=YOUR_TOKEN
python scripts\01_download_sf_cad.py
```

في PowerShell:
```powershell
$env:SF_APP_TOKEN="YOUR_TOKEN"
python scripts\01_download_sf_cad.py
```

لا تضعي الـtoken داخل الكود ولا ترسليه في المحادثة.

### ملاحظة عن Python 3.8

الأمر الذي ظهر في رسالة الخطأ يستخدم `Python 3.8`. هذا لا يسبب خطأ 403 نفسه، لكن إصدارات الحزم الحديثة في `requirements.txt` موجهة عمليًا إلى Python أحدث. لتشغيل المشروع كاملًا يفضل استخدام Python 3.10 أو 3.11.

## التشغيل بالترتيب

```text
1) scripts/00_install.bat
2) scripts/01_download_sf_cad.py
3) scripts/02_prepare_real_data.py
4) scripts/03_validate_and_select_models.py
5) scripts/04_build_incident_resource_matrix.py
6) scripts/05_score_pairs_with_ai.py
7) scripts/06_run_shap.py
8) scripts/07_compare_strategies.py
9) scripts/08_statistical_tests.py
10) scripts/09_scalability.py
11) streamlit run app.py
```

للتشغيل السهل على Windows استخدمي `run_stage2.bat` بعد تثبيت Python.

## ملاحظة مهمة حول القاهرة ومصر

هذه النسخة تستخدم **بيانات تشغيل حقيقية من خارج مصر** كمرجع عملي لتقييم AI/Optimization لأن سجلات EAO التشغيلية التفصيلية ليست قاعدة بيانات عامة قابلة للتنزيل. يمكن إضافة Cairo traffic/climate كمعلومات سياقية منفصلة، لكن لا ينبغي وصف بيانات San Francisco بأنها بيانات مصرية.

## ملاحظة منهجية حول Severity

في هذا المشروع الأساسي، `final_priority` هو **Operational Dispatch Priority** وليس تشخيصًا طبيًا ولا Severity سريريًا. إذا أصبح لدى المشروع المصري مستقبلًا label طبي/triage معتمد، يتم استبدال الهدف مع بقاء البنية البرمجية نفسها تقريبًا.
