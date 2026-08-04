import importlib
import sys
from pathlib import Path


def check_opportunity_engine():
    print("=" * 60)
    print("🔍 بدء فحص وتفعيل محرك الفرص (Opportunity Engine)")
    print("=" * 60)

    # 1. تحديد المسارات وتحقق المجلد الرئيسي
    root_dir = Path(__file__).resolve().parent
    opportunity_dir = root_dir / "backend" / "opportunity"

    print(f"📂 مسار المشروع الرئيسي: {root_dir}")
    print(f"📂 مسار محرك الفرص:     {opportunity_dir}\n")

    if not opportunity_dir.exists():
        print(f"❌ خطأ: المجلد غير موجود! -> {opportunity_dir}")
        return

    # إضافة مجلد الجذر ومجلد backend لـ sys.path لتفادي أخطاء الاستيراد
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    # 2. قائمة الملفات المطلوبة
    required_files = [
        "__init__.py",  # التنويه: التأكد من الشرطتين السفليتين
        "opportunity_engine.py",
        "models.py",
        "phase_detector.py",
        "transition_model.py",
        "catalyst_engine.py",
        "timeline.py",
        "confidence.py",
        "scoring.py",
        "explanation.py",
        "probability.py",
    ]

    print("📄 1. التحقق من وجود الملفات:")
    print("-" * 40)

    missing_files = []
    for file_name in required_files:
        file_path = opportunity_dir / file_name
        if file_path.is_file():
            print(f"  ✅ {file_name:<25} (موجود)")
        else:
            print(f"  ❌ {file_name:<25} (غير موجود!)")
            missing_files.append(file_name)

    if missing_files:
        print(
            f"\n⚠️ توقف الفحص: هناك {len(missing_files)} ملف/ملفات مفقودة. يرجى إنشاؤها أولاً."
        )
        return

    print("\n📦 2. اختبار استيراد الوحدات (Module Imports):")
    print("-" * 40)

    # 3. اختبار استيراد كل ملف بشكل مستقل
    import_errors = 0
    modules_to_test = [
        "backend.opportunity.models",
        "backend.opportunity.phase_detector",
        "backend.opportunity.transition_model",
        "backend.opportunity.catalyst_engine",
        "backend.opportunity.timeline",
        "backend.opportunity.confidence",
        "backend.opportunity.scoring",
        "backend.opportunity.explanation",
        "backend.opportunity.probability",
        "backend.opportunity.opportunity_engine",
    ]

    for mod_name in modules_to_test:
        try:
            importlib.import_module(mod_name)
            print(f"  ✅ استيراد ناجح: {mod_name}")
        except Exception as e:
            print(f"  ❌ فشل استيراد: {mod_name}")
            print(f"     └─ السبب: {type(e).__name__}: {e}")
            import_errors += 1

    print("\n🚀 3. اختبار استيراد الحزمة الرئيسية (backend.opportunity):")
    print("-" * 40)

    try:
        import backend.opportunity as opp

        print("  ✅ تم استيراد الحزمة الرئيسية بنجاح!")

        # طباعة المحتويات المصدرة من __init__.py إن وجدت
        exported = getattr(opp, "__all__", [x for x in dir(opp) if not x.startswith("_")])
        print(f"  ℹ️ العناصر المصدرة المتاحة ({len(exported)}): {exported}")

    except Exception as e:
        print("  ❌ فشل استيراد الحزمة الرئيسية عبر __init__.py")
        print(f"     └─ السبب: {type(e).__name__}: {e}")
        import_errors += 1

    # 4. النتيجة النهائية
    print("\n" + "=" * 60)
    if import_errors == 0:
        print(
            "🎉 اكتمل الفحص بنجاح! محرك الفرص جاهز للعمل ولا توجد أخطاء استيراد."
        )
    else:
        print(f"⚠️ اكتمل الفحص مع وجود {import_errors} خطأ/أخطاء يحتاج إلى معالجة.")
    print("=" * 60)


if __name__ == "__main__":
    check_opportunity_engine()
