# MarketingFlow: قرار استقلال المنتج والاستفادة من SaaS Core Kit

> **التاريخ:** 2026-08-17  
> **الحالة:** معتمد من المستخدم  
> **النوع:** Product Boundary / Architecture Decision

## القرار

MarketingFlow منتج مستقل كامل، وليس موديولًا جديدًا داخل MVC Starter Kit
الحالي. يملك repository ودومين وقاعدة بيانات ونشرًا وsecrets ونسخًا احتياطية
مستقلة، مع الاستفادة من Reusable SaaS Core Kit المستخرج من الأنماط المثبتة في
MVC.

## حدود المنتج

هذه القدرات تنتمي معًا إلى MarketingFlow ولا تُفصل إلى مواقع مستقلة:

- Auth وإدارة الحساب.
- مساحات العملاء وBrand Knowledge.
- الحملات وحالتها وإمكانية الاستكمال.
- Direct-response strategy وcontent generation وreview.
- Content library وfeedback memory.
- Hash/semantic anti-duplication وإعادة كتابة واحدة عند الحاجة.

المنتجات ذات الجمهور والوعد والبراند ودورة التشغيل المختلفة—مثل Website
Builder وVectorizer وCode Audit—تبقى مشاريع شقيقة مستقلة.

## إعادة استخدام ما تم بناؤه

- كود LangGraph الحالي وschemas والاختبارات والـprompts مرجع محرك موثوق، ولا
  يُرمى أو يُعاد اختراعه بلا سبب.
- Streamlit يبقى prototype محليًا حتى اعتماد واجهة الإنتاج؛ ليس قرار النشر
  النهائي.
- Supabase foundation المكتوبة تبقى محفوظة، لكن تفعيلها مجمد؛ لا تُطلب
  credentials قبل حسم بنية المنتج المشتقة من Core Kit.
- لا يُنقل MVC الحالي بالكامل، ولا تُنسخ موديولات منتجاته إلى MarketingFlow.

## العلاقة مع MVC وCore Kit

المصدر الحاكم لسياسة الاستخراج وحدود القالب هو:

`MVC Starter Kit/docs/superpowers/specs/2026-08-17-reusable-saas-core-and-product-boundaries-decision.md`

MarketingFlow يستهلك إصدارًا مثبتًا من الـCore Kit بعد استخراجه واختباره، ثم
يضيف نطاقه فقط. لا توجد قاعدة بيانات أو deployment أو runtime مشتركة مع MVC.

## قرار ما زال مطلوبًا قبل التنفيذ

يجب تحديد التموضع التجاري النهائي بين MarketingFlow وسِدر:

- إذا كان MarketingFlow self-service وسِدر done-for-you فهما منتجان شقيقان.
- إذا كانا يخدمان نفس العميل بنفس النتيجة، يصبح MarketingFlow تطورًا/بديلًا
  لسِدر بدل تشغيل منتجين متداخلين.

هذا القرار يؤثر في الاسم والرسائل والتسعير، لكنه لا يغير قرار الاستقلال عن MVC.

## نقطة الاستئناف

1. إغلاق تغييرات MVC المحلية الجارية.
2. تصميم واستخراج SaaS Core Kit v1 في جلسة مستقلة.
3. حسم علاقة MarketingFlow وسِدر.
4. كتابة خطة تحويل MarketingFlow إلى المنتج المستقل المشتق من القالب.

