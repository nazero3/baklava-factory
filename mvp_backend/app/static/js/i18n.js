(function (global) {
  const LANG_KEY = "baklava_lang";
  const SUPPORTED = ["en", "ar"];
  const RTL_LANGS = ["ar"];

  const DICT = {
    en: {
      "app.name": "Baklava Factory",
      "app.tagline": "Manufacturing & Warehouse Management",

      // Nav groups
      "nav.group.main": "Main",
      "nav.group.operate": "Operate",
      "nav.group.catalog": "Catalog",
      "nav.group.insights": "Insights",
      "nav.group.admin": "Admin",

      // Nav items
      "nav.dashboard": "Dashboard",
      "nav.receiving": "Receiving",
      "nav.production": "Production",
      "nav.dispatch": "Dispatch",
      "nav.store_movements": "Store Movements",
      "nav.suppliers": "Suppliers",
      "nav.stores": "Stores",
      "nav.products": "Products",
      "nav.recipes": "Recipes",
      "nav.inventory": "Inventory",
      "nav.approvals": "Approvals",
      "nav.reports": "Reports",
      "nav.users": "Users",

      // Common
      "common.logout": "Logout",
      "common.loading": "Loading…",
      "common.save": "Save",
      "common.cancel": "Cancel",
      "common.submit": "Submit",
      "common.create": "Create",
      "common.add": "Add",
      "common.approve": "Approve",
      "common.reject": "Reject",
      "common.refresh": "Refresh",
      "common.actions": "Actions",
      "common.status": "Status",
      "common.id": "ID",
      "common.code": "Code",
      "common.name": "Name",
      "common.unit": "Unit",
      "common.qty_kg": "Quantity (kg)",
      "common.unit_cost": "Unit cost",
      "common.product": "Product",
      "common.supplier": "Supplier",
      "common.store": "Store",
      "common.none": "—",
      "common.select": "— Select —",
      "common.optional": "Optional",
      "common.required": "Required",
      "common.created_at": "Created",
      "common.reason": "Reason",
      "common.export_csv": "Export CSV",
      "common.value": "Value",
      "common.lang_toggle": "العربية",

      // Login
      "login.title": "Baklava Factory",
      "login.subtitle": "Sign in to continue",
      "login.username": "Username",
      "login.password": "Password",
      "login.signin": "Sign in",
      "login.signing_in": "Signing in…",
      "login.welcome": "Welcome",
      "login.failed": "Login failed",

      // Dashboard
      "dash.title": "Dashboard",
      "dash.subtitle": "Live overview of factory operations",
      "dash.kpi.raw_stock": "Raw stock",
      "dash.kpi.finished_stock": "Finished stock",
      "dash.kpi.inventory_value": "Inventory value",
      "dash.kpi.produced": "Produced (total)",
      "dash.kpi.waste": "Waste (total)",
      "dash.kpi.sales": "Sales (total)",
      "dash.kpi.pending_approvals": "Pending approvals",
      "dash.kpi.low_stock": "Low-stock items",
      "dash.alerts.title": "Alerts",
      "dash.alerts.low_stock": "Low stock",
      "dash.alerts.none": "No alerts. Everything looks healthy.",
      "dash.alerts.approvals_pending": "items awaiting approval",
      "dash.activity.title": "Recent activity",
      "dash.activity.none": "No recent activity yet.",
      "dash.quick.title": "Quick actions",

      // Activity / movement types
      "type.receiving": "Receiving",
      "type.production": "Production",
      "type.transfer": "Transfer",
      "type.sale": "Sale",
      "type.return": "Return",
      "type.waste": "Waste",
      "type.adjustment": "Adjustment",

      // Suppliers
      "suppliers.title": "Suppliers",
      "suppliers.subtitle": "Register suppliers you buy raw materials from.",
      "suppliers.add": "Add supplier",
      "suppliers.name": "Supplier name",
      "suppliers.list": "Supplier list",
      "suppliers.empty": "No suppliers yet. Create one above.",
      "suppliers.created": "Supplier created",

      // Stores
      "stores.title": "Stores",
      "stores.subtitle": "Retail / distribution locations that receive finished goods.",
      "stores.add": "Add store",
      "stores.name": "Store name",
      "stores.list": "Store list",
      "stores.empty": "No stores yet. Create one above.",
      "stores.created": "Store created",

      // Products
      "products.title": "Products",
      "products.subtitle": "Define raw materials and finished goods.",
      "products.add": "Add product",
      "products.category": "Category",
      "products.category.raw": "Raw material",
      "products.category.finished": "Finished good",
      "products.reorder_level": "Reorder level (kg)",
      "products.reorder_help": "Low-stock alert triggers below this quantity. 0 disables it.",
      "products.list": "Product catalog",
      "products.empty": "No products yet. Create one above.",
      "products.created": "Product created",
      "products.factory_stock": "Factory stock (kg)",
      "products.filter_all": "All categories",

      // Recipes
      "recipes.title": "Recipes",
      "recipes.subtitle": "Define how much of each raw material is consumed per 1 kg of finished output.",
      "recipes.finished": "Finished product",
      "recipes.ingredient": "Raw material",
      "recipes.qty_per_kg": "Qty per kg output",
      "recipes.add_ingredient": "Add ingredient",
      "recipes.remove": "Remove",
      "recipes.save": "Save recipe",
      "recipes.saved": "Recipe saved",
      "recipes.list": "Existing recipes",
      "recipes.empty": "No recipes yet.",
      "recipes.ingredients": "Ingredients",
      "recipes.need_one": "Add at least one ingredient.",

      // Receiving
      "recv.title": "Receiving",
      "recv.subtitle": "Record incoming goods from a supplier into warehouse inventory.",
      "recv.lot_no": "Lot number",
      "recv.post": "Post receiving",
      "recv.posted": "Receiving posted",
      "recv.recent": "Recent receivings",
      "recv.empty": "No receivings yet.",

      // Production
      "prod.title": "Production",
      "prod.subtitle": "Consume raw materials per recipe and add finished goods to factory stock.",
      "prod.target_kg": "Target (kg)",
      "prod.actual_kg": "Actual output (kg)",
      "prod.waste_kg": "Waste (kg)",
      "prod.run": "Complete batch",
      "prod.done": "Batch completed",
      "prod.recent": "Recent batches",
      "prod.empty": "No production batches yet.",
      "prod.consumed": "Consumed",

      // Dispatch
      "disp.title": "Dispatch Transfer",
      "disp.subtitle": "Send finished goods from the warehouse to a store.",
      "disp.dispatch": "Dispatch transfer",
      "disp.dispatched": "Transfer dispatched",
      "disp.receive_title": "Receive Transfer",
      "disp.receive_subtitle": "Confirm goods arrived at the store.",
      "disp.transfer": "Transfer",
      "disp.received_qty": "Received qty (kg)",
      "disp.confirm": "Confirm receipt",
      "disp.received": "Transfer received",
      "disp.recent": "Recent transfers",
      "disp.empty": "No transfers yet.",
      "disp.to_store": "Destination store",

      // Store movements
      "store.title": "Store Movements",
      "store.subtitle": "Record sales, returns, and waste at a store location.",
      "store.movement_type": "Movement type",
      "store.post": "Post movement",
      "store.posted": "Movement posted",
      "store.recent": "Recent movements",
      "store.empty": "No movements yet.",

      // Inventory
      "inv.title": "Inventory",
      "inv.subtitle": "Stock on hand across the factory and stores, with valuation.",
      "inv.location": "Location",
      "inv.location_type": "Location type",
      "inv.cost_per_kg": "Cost / kg",
      "inv.empty": "No inventory yet.",
      "inv.factory": "Factory",
      "inv.total_value": "Total inventory value",
      "inv.adjust": "Request adjustment",
      "inv.adjust_title": "Inventory adjustment",
      "inv.qty_delta": "Adjustment (+/- kg)",

      // Approvals
      "appr.title": "Approvals",
      "appr.subtitle": "Review pending inventory adjustments and transfer exceptions.",
      "appr.adjustments": "Inventory adjustments",
      "appr.exceptions": "Transfer exceptions",
      "appr.expected": "Expected",
      "appr.received": "Received",
      "appr.difference": "Difference",
      "appr.delta": "Delta (kg)",
      "appr.empty_adj": "No inventory adjustments.",
      "appr.empty_exc": "No transfer exceptions.",
      "appr.approved": "Approved",
      "appr.rejected": "Rejected",

      // Reports
      "reports.title": "Reports",
      "reports.subtitle": "Operational and financial summaries.",
      "reports.type": "Report",
      "reports.inventory_value": "Inventory value by category",
      "reports.low_stock": "Low-stock items",
      "reports.transfer_exceptions": "Transfer exceptions",
      "reports.production_yield": "Production yield & waste",
      "reports.run": "Run report",
      "reports.empty": "No data for this report.",
      "reports.category": "Category",
      "reports.total_qty": "Total qty (kg)",
      "reports.total_value": "Total value",
      "reports.yield_pct": "Yield %",

      // Users
      "users.title": "Users & Roles",
      "users.subtitle": "Create accounts and assign roles.",
      "users.add": "Add user",
      "users.username": "Username",
      "users.full_name": "Full name",
      "users.password": "Password",
      "users.role": "Role",
      "users.list": "User list",
      "users.empty": "No users yet.",
      "users.created": "User created",
      "users.active": "Active",

      // Roles
      "role.admin": "Administrator",
      "role.executive": "Executive",
      "role.factory_manager": "Factory Manager",
      "role.warehouse": "Warehouse",
      "role.production_supervisor": "Production Supervisor",
      "role.store_manager": "Store Manager",
      "role.accountant": "Accountant"
    },
    ar: {
      "app.name": "مصنع البقلاوة",
      "app.tagline": "إدارة التصنيع والمستودعات",

      "nav.group.main": "الرئيسية",
      "nav.group.operate": "التشغيل",
      "nav.group.catalog": "الكتالوج",
      "nav.group.insights": "التحليلات",
      "nav.group.admin": "الإدارة",

      "nav.dashboard": "لوحة التحكم",
      "nav.receiving": "الاستلام",
      "nav.production": "الإنتاج",
      "nav.dispatch": "الإرسال",
      "nav.store_movements": "حركات المتجر",
      "nav.suppliers": "الموردون",
      "nav.stores": "المتاجر",
      "nav.products": "المنتجات",
      "nav.recipes": "الوصفات",
      "nav.inventory": "المخزون",
      "nav.approvals": "الموافقات",
      "nav.reports": "التقارير",
      "nav.users": "المستخدمون",

      "common.logout": "تسجيل الخروج",
      "common.loading": "جارٍ التحميل…",
      "common.save": "حفظ",
      "common.cancel": "إلغاء",
      "common.submit": "إرسال",
      "common.create": "إنشاء",
      "common.add": "إضافة",
      "common.approve": "موافقة",
      "common.reject": "رفض",
      "common.refresh": "تحديث",
      "common.actions": "إجراءات",
      "common.status": "الحالة",
      "common.id": "المعرّف",
      "common.code": "الرمز",
      "common.name": "الاسم",
      "common.unit": "الوحدة",
      "common.qty_kg": "الكمية (كغ)",
      "common.unit_cost": "تكلفة الوحدة",
      "common.product": "المنتج",
      "common.supplier": "المورّد",
      "common.store": "المتجر",
      "common.none": "—",
      "common.select": "— اختر —",
      "common.optional": "اختياري",
      "common.required": "مطلوب",
      "common.created_at": "تاريخ الإنشاء",
      "common.reason": "السبب",
      "common.export_csv": "تصدير CSV",
      "common.value": "القيمة",
      "common.lang_toggle": "English",

      "login.title": "مصنع البقلاوة",
      "login.subtitle": "سجّل الدخول للمتابعة",
      "login.username": "اسم المستخدم",
      "login.password": "كلمة المرور",
      "login.signin": "تسجيل الدخول",
      "login.signing_in": "جارٍ تسجيل الدخول…",
      "login.welcome": "مرحباً",
      "login.failed": "فشل تسجيل الدخول",

      "dash.title": "لوحة التحكم",
      "dash.subtitle": "نظرة حية على عمليات المصنع",
      "dash.kpi.raw_stock": "المواد الخام",
      "dash.kpi.finished_stock": "المنتجات الجاهزة",
      "dash.kpi.inventory_value": "قيمة المخزون",
      "dash.kpi.produced": "إجمالي الإنتاج",
      "dash.kpi.waste": "إجمالي الهدر",
      "dash.kpi.sales": "إجمالي المبيعات",
      "dash.kpi.pending_approvals": "موافقات معلّقة",
      "dash.kpi.low_stock": "أصناف منخفضة المخزون",
      "dash.alerts.title": "التنبيهات",
      "dash.alerts.low_stock": "مخزون منخفض",
      "dash.alerts.none": "لا توجد تنبيهات. كل شيء على ما يرام.",
      "dash.alerts.approvals_pending": "عناصر بانتظار الموافقة",
      "dash.activity.title": "النشاط الأخير",
      "dash.activity.none": "لا يوجد نشاط حديث بعد.",
      "dash.quick.title": "إجراءات سريعة",

      "type.receiving": "استلام",
      "type.production": "إنتاج",
      "type.transfer": "تحويل",
      "type.sale": "بيع",
      "type.return": "إرجاع",
      "type.waste": "هدر",
      "type.adjustment": "تسوية",

      "suppliers.title": "الموردون",
      "suppliers.subtitle": "سجّل الموردين الذين تشتري منهم المواد الخام.",
      "suppliers.add": "إضافة مورّد",
      "suppliers.name": "اسم المورّد",
      "suppliers.list": "قائمة الموردين",
      "suppliers.empty": "لا يوجد موردون بعد. أضف واحداً بالأعلى.",
      "suppliers.created": "تم إنشاء المورّد",

      "stores.title": "المتاجر",
      "stores.subtitle": "مواقع البيع والتوزيع التي تستلم المنتجات الجاهزة.",
      "stores.add": "إضافة متجر",
      "stores.name": "اسم المتجر",
      "stores.list": "قائمة المتاجر",
      "stores.empty": "لا توجد متاجر بعد. أضف واحداً بالأعلى.",
      "stores.created": "تم إنشاء المتجر",

      "products.title": "المنتجات",
      "products.subtitle": "تعريف المواد الخام والمنتجات الجاهزة.",
      "products.add": "إضافة منتج",
      "products.category": "الفئة",
      "products.category.raw": "مادة خام",
      "products.category.finished": "منتج جاهز",
      "products.reorder_level": "حد إعادة الطلب (كغ)",
      "products.reorder_help": "ينطلق تنبيه نقص المخزون تحت هذه الكمية. القيمة 0 تعطّله.",
      "products.list": "كتالوج المنتجات",
      "products.empty": "لا توجد منتجات بعد. أضف واحداً بالأعلى.",
      "products.created": "تم إنشاء المنتج",
      "products.factory_stock": "مخزون المصنع (كغ)",
      "products.filter_all": "كل الفئات",

      "recipes.title": "الوصفات",
      "recipes.subtitle": "حدّد كمية كل مادة خام المستهلكة لكل 1 كغ من المنتج الجاهز.",
      "recipes.finished": "المنتج الجاهز",
      "recipes.ingredient": "المادة الخام",
      "recipes.qty_per_kg": "كمية لكل كغ إنتاج",
      "recipes.add_ingredient": "إضافة مكوّن",
      "recipes.remove": "حذف",
      "recipes.save": "حفظ الوصفة",
      "recipes.saved": "تم حفظ الوصفة",
      "recipes.list": "الوصفات الحالية",
      "recipes.empty": "لا توجد وصفات بعد.",
      "recipes.ingredients": "المكوّنات",
      "recipes.need_one": "أضف مكوّناً واحداً على الأقل.",

      "recv.title": "الاستلام",
      "recv.subtitle": "سجّل البضائع الواردة من مورّد إلى مخزون المستودع.",
      "recv.lot_no": "رقم الدفعة",
      "recv.post": "تسجيل الاستلام",
      "recv.posted": "تم تسجيل الاستلام",
      "recv.recent": "الاستلامات الأخيرة",
      "recv.empty": "لا توجد استلامات بعد.",

      "prod.title": "الإنتاج",
      "prod.subtitle": "استهلاك المواد الخام حسب الوصفة وإضافة المنتجات الجاهزة لمخزون المصنع.",
      "prod.target_kg": "الهدف (كغ)",
      "prod.actual_kg": "الإنتاج الفعلي (كغ)",
      "prod.waste_kg": "الهدر (كغ)",
      "prod.run": "إتمام الدفعة",
      "prod.done": "تم إتمام الدفعة",
      "prod.recent": "الدفعات الأخيرة",
      "prod.empty": "لا توجد دفعات إنتاج بعد.",
      "prod.consumed": "المستهلك",

      "disp.title": "إرسال تحويل",
      "disp.subtitle": "إرسال المنتجات الجاهزة من المستودع إلى متجر.",
      "disp.dispatch": "إرسال التحويل",
      "disp.dispatched": "تم إرسال التحويل",
      "disp.receive_title": "استلام تحويل",
      "disp.receive_subtitle": "تأكيد وصول البضائع إلى المتجر.",
      "disp.transfer": "التحويل",
      "disp.received_qty": "الكمية المستلمة (كغ)",
      "disp.confirm": "تأكيد الاستلام",
      "disp.received": "تم استلام التحويل",
      "disp.recent": "التحويلات الأخيرة",
      "disp.empty": "لا توجد تحويلات بعد.",
      "disp.to_store": "المتجر الوجهة",

      "store.title": "حركات المتجر",
      "store.subtitle": "تسجيل المبيعات والمرتجعات والهدر في موقع متجر.",
      "store.movement_type": "نوع الحركة",
      "store.post": "تسجيل الحركة",
      "store.posted": "تم تسجيل الحركة",
      "store.recent": "الحركات الأخيرة",
      "store.empty": "لا توجد حركات بعد.",

      "inv.title": "المخزون",
      "inv.subtitle": "المخزون المتاح في المصنع والمتاجر مع التقييم.",
      "inv.location": "الموقع",
      "inv.location_type": "نوع الموقع",
      "inv.cost_per_kg": "التكلفة / كغ",
      "inv.empty": "لا يوجد مخزون بعد.",
      "inv.factory": "المصنع",
      "inv.total_value": "إجمالي قيمة المخزون",
      "inv.adjust": "طلب تسوية",
      "inv.adjust_title": "تسوية المخزون",
      "inv.qty_delta": "التسوية (+/- كغ)",

      "appr.title": "الموافقات",
      "appr.subtitle": "مراجعة تسويات المخزون واستثناءات التحويل المعلّقة.",
      "appr.adjustments": "تسويات المخزون",
      "appr.exceptions": "استثناءات التحويل",
      "appr.expected": "المتوقع",
      "appr.received": "المستلم",
      "appr.difference": "الفرق",
      "appr.delta": "الفرق (كغ)",
      "appr.empty_adj": "لا توجد تسويات مخزون.",
      "appr.empty_exc": "لا توجد استثناءات تحويل.",
      "appr.approved": "تمت الموافقة",
      "appr.rejected": "مرفوض",

      "reports.title": "التقارير",
      "reports.subtitle": "ملخصات تشغيلية ومالية.",
      "reports.type": "التقرير",
      "reports.inventory_value": "قيمة المخزون حسب الفئة",
      "reports.low_stock": "الأصناف منخفضة المخزون",
      "reports.transfer_exceptions": "استثناءات التحويل",
      "reports.production_yield": "إنتاجية الإنتاج والهدر",
      "reports.run": "تشغيل التقرير",
      "reports.empty": "لا توجد بيانات لهذا التقرير.",
      "reports.category": "الفئة",
      "reports.total_qty": "إجمالي الكمية (كغ)",
      "reports.total_value": "إجمالي القيمة",
      "reports.yield_pct": "نسبة الإنتاجية %",

      "users.title": "المستخدمون والأدوار",
      "users.subtitle": "إنشاء الحسابات وتعيين الأدوار.",
      "users.add": "إضافة مستخدم",
      "users.username": "اسم المستخدم",
      "users.full_name": "الاسم الكامل",
      "users.password": "كلمة المرور",
      "users.role": "الدور",
      "users.list": "قائمة المستخدمين",
      "users.empty": "لا يوجد مستخدمون بعد.",
      "users.created": "تم إنشاء المستخدم",
      "users.active": "نشط",

      "role.admin": "مدير النظام",
      "role.executive": "تنفيذي",
      "role.factory_manager": "مدير المصنع",
      "role.warehouse": "مستودع",
      "role.production_supervisor": "مشرف إنتاج",
      "role.store_manager": "مدير متجر",
      "role.accountant": "محاسب"
    }
  };

  function getLang() {
    const stored = localStorage.getItem(LANG_KEY);
    return SUPPORTED.includes(stored) ? stored : "en";
  }

  function isRtl(lang) {
    return RTL_LANGS.includes(lang || getLang());
  }

  function t(key, fallback) {
    const lang = getLang();
    const table = DICT[lang] || DICT.en;
    if (key in table) return table[key];
    if (key in DICT.en) return DICT.en[key];
    return fallback !== undefined ? fallback : key;
  }

  function applyDir() {
    const lang = getLang();
    document.documentElement.lang = lang;
    document.documentElement.dir = isRtl(lang) ? "rtl" : "ltr";
  }

  // Translate any element that carries data-i18n / data-i18n-placeholder / data-i18n-title.
  function translateDom(root) {
    const scope = root || document;
    scope.querySelectorAll("[data-i18n]").forEach((el) => {
      el.textContent = t(el.getAttribute("data-i18n"));
    });
    scope.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      el.setAttribute("placeholder", t(el.getAttribute("data-i18n-placeholder")));
    });
    scope.querySelectorAll("[data-i18n-title]").forEach((el) => {
      el.setAttribute("title", t(el.getAttribute("data-i18n-title")));
    });
    if (scope === document) {
      const titleKey = document.documentElement.getAttribute("data-i18n-doctitle");
      if (titleKey) document.title = t(titleKey) + " — " + t("app.name");
    }
  }

  function apply(root) {
    applyDir();
    translateDom(root);
  }

  function setLang(lang) {
    if (!SUPPORTED.includes(lang)) return;
    localStorage.setItem(LANG_KEY, lang);
    window.location.reload();
  }

  function toggleLang() {
    setLang(getLang() === "ar" ? "en" : "ar");
  }

  // Apply direction as early as possible to avoid flash of wrong direction.
  applyDir();

  global.BaklavaI18n = {
    t,
    getLang,
    setLang,
    toggleLang,
    isRtl,
    apply,
    translateDom,
    SUPPORTED
  };
})(window);
