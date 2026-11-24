# AGENTS.md — MarketingFlow AI
> ملف الحالة الحي للمشروع. التحديث يكون بإضافات دقيقة، لا بإعادة بناء الملف.
> آخر تحديث: 2026-08-17

## 1. تعريف سريع
- **المشروع:** منصة تسويق متعددة الوكلاء مبنية على LangGraph وGemini وStreamlit.
- **المرحلة الحالية:** تم اعتماد MarketingFlow كمنتج مستقل؛ مسار Supabase/Streamlit الإنتاجي مجمد حتى استخراج Reusable SaaS Core Kit وحسم تموضع المنتج مع سِدر.
- **SSOT الحالي:** `docs/superpowers/specs/2026-08-17-independent-product-and-core-kit-decision.md`
- **تصميم V3 السابق:** `docs/superpowers/specs/2026-08-16-marketingflow-v3-upgrade-design.md` مرجع لما تم بناؤه، وليس قرار النشر الحالي.
- **قاعدة الجلسات:** كل جلسة تبدأ من نقطة الاستئناف وتنتهي بتحديثها.

## 2. حالة التنفيذ
| المكوّن | الحالة | ملاحظات |
|---|---|---|
| V2 الحالية | ✅ | تعمل من `app.py` والـLangGraph قابل للاستيراد |
| مراجعة V3 ZIP | ✅ | فُحصت كمرجع؛ ممنوع نسخها بالكامل فوق المشروع |
| تصميم الترقية | ✅ | اعتمده المستخدم في 2026-08-16 |
| Baseline واختبارات الحماية | ✅ | 18 اختبارًا offline ناجحًا وStreamlit health = ok |
| Workflow contracts/correctness | ✅ | 29 اختبارًا؛ reviewer correction وfail-closed وrewrite واحد |
| Supabase foundation/Auth code | ✅ | migration + RLS + private Storage + Auth service/UI + scoped repository |
| Supabase live integration | ⏸️ | مجمد بقرار 2026-08-17؛ لا credentials مطلوبة قبل حسم معمارية المنتج المستقل |
| Product boundary/Core Kit decision | ✅ | MarketingFlow مستقل؛ لا يدمج داخل MVC الحالي ولا يبدأ من نسخة MVC المتضخمة |

### نقطة الاستئناف
```text
► صمّم واستخرج Reusable SaaS Core Kit v1 بعد إغلاق تغييرات MVC الجارية، ثم احسم علاقة MarketingFlow بسِدر واكتب خطة المنتج المستقل.
```

### على المستخدم
- [ ] لا credentials مطلوبة الآن؛ تكامل Supabase مجمد لحين حسم بنية المنتج النهائية.

## 3. قرارات معتمدة
1. المشروع الحالي في `/Users/imac/IMac/Mo/projects/Ai/marketingflow_ai` هو الـmaster الوحيد.
2. ندمج من V3 انتقائيًا؛ لا `rsync` ولا استبدال شامل للملفات.
3. نحافظ على Streamlit + LangGraph + Gemini، ونستخدم Supabase للخدمات الدائمة.
4. Google وemail/password يمران عبر Supabase Auth بهوية موحدة.
5. بيانات المستخدم تستخدم JWT المستخدم وRLS؛ لا يُستخدم Supabase secret/service key في مسار طلبات التطبيق.
6. الأداء والتكلفة: تخزين embeddings والبحث والنتائج، وعدم إعادة البحث أو التوليد دون سبب.
7. Novelty يبدأ بفحص hash/vector؛ استدعاء LLM وإعادة الكتابة مرة واحدة فقط عند اكتشاف تشابه فعلي.
8. واجهة Streamlit تعتمد العناصر الأصلية وcaching/fragments/forms، وتتجنب HTML/CSS والمكوّنات الخارجية إلا لضرورة مثبتة.
9. SQLite ليس مسار إنتاج موازيًا؛ يؤجل ولا يضاف إلا إذا ظهر احتياج حقيقي لديمو محلي مستقل.
10. اعتماد المستخدم يشمل الاستمرار التلقائي بين المراحل؛ checkpoints داخلية، والتوقف فقط عند blocker خارجي حقيقي.
11. Google OIDC تديره Streamlit ثم يُبادل ID token داخل Supabase؛ هوية وملكية البيانات النهائية هي Supabase UUID.
12. **قرار ناسخ بتاريخ 2026-08-17:** البنود 3-5 و8 و11 تصف prototype/مسار V3 السابق، وليست معمارية الإنتاج المعتمدة حاليًا؛ والبندان 1-2 يحميان كود Python الحالي كمرجع للمحرك لا باعتباره مستودع واجهة الإنتاج النهائية.
13. MarketingFlow منتج مستقل كامل، لا موديول داخل MVC الحالي، ويملك repository ودومين وقاعدة بيانات ونشرًا مستقلًا.
14. MVC الحالي لا يُنسخ بالكامل؛ يُستخرج منه Reusable SaaS Core Kit نظيف ومختبر، ثم يبدأ MarketingFlow من إصدار مثبت منه.
15. الفصل يكون حسب المنتج ذي القيمة والجمهور ودورة التشغيل المستقلة، لا حسب كل Feature؛ Auth والعملاء والحملات والذاكرة والـanti-duplication تظل داخل MarketingFlow.
16. كود LangGraph والـschemas والاختبارات والـprompts الحالية محفوظة كمرجع للمحرك، وStreamlit يبقى prototype حتى قرار الواجهة الإنتاجية.

## 4. سجل الدروس
| # | التاريخ | الدرس/الخطأ | التصحيح المعتمد |
|---|---|---|---|
| L1 | 2026-08-16 | الادعاء بأن ZIP منفصل مطبق محليًا غير كافٍ | الملفات الفعلية وGit هما الحكم |
| L2 | 2026-08-16 | خلط Streamlit OIDC مع Supabase email يصنع هويتين | Supabase Auth موحد لكل طرق الدخول |
| L3 | 2026-08-16 | service key يلغي قيمة RLS | publishable key + user JWT + سياسات RLS فعلية |
| L4 | 2026-08-16 | كتابة التصحيح داخل ملاحظات reviewer لا تغيّر التسليم | approved/corrected content حقل مستقل وهو المصدر الوحيد للـfinalizer |

## 5. أفكار مؤجلة
- Offline SQLite adapter إذا أصبح مطلوبًا فعلًا.
- LangSmith managed deployment.
- Background workers وqueues.
- Welcome email مخصص لمستخدمي Google.
- فرق متعددة وصلاحيات إدارية.
- SSO مركزي بين المنتجات؛ لا يضاف قبل ظهور حاجة تشغيلية حقيقية.
- تحويل القدرات الاختيارية في Core Kit إلى packages؛ لا يحدث قبل استعمالين مستقلين مثبتين.

## 6. مخاطر مفتوحة
| الخطر | الحالة |
|---|---|
| OAuth callback/session داخل Streamlit | مؤجل؛ يخص prototype وليس مسار الإنتاج الحالي |
| لا توجد بيانات Supabase تجريبية أو credentials | مؤجل؛ لا تُطلب أثناء تجميد هذا المسار |
| Gemini 2.5 Flash في المشروع الحالي يقترب من الإيقاف | 🟡 |
| V3 ZIP غير مختبرة وتشمل نقاط ضعف أمنية ومعمارية | 🟡 |
| تداخل التموضع التجاري بين MarketingFlow وسِدر لم يُحسم بعد | 🟡 |
| تعدد المستودعات قد يسبب drift في إصلاحات الأمان إن لم تُدار إصدارات الـCore | 🟡 |

## 7. بروتوكول التحديث
- يُحدّث عند قفل كل جلسة أو اعتماد قرار/درس جديد.
- لا تُحذف القرارات أو الدروس دون إذن صريح.
- أي فكرة جانبية تُسجل في «أفكار مؤجلة» بدل توسيع المهمة الحالية.

🔔 **"حدّث"/lessons trigger:** درس خاص بـ MarketingFlow AI ← قسم الدروس/القرارات في هذا الملف. درس عام قابل لإعادة الاستخدام في أي مشروع تاني (بغض النظر عن الستاك) ← يترقّى لـ `team-ai-skills/skills/core-engineering/references/improvement-log.md`.
