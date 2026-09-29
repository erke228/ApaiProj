"""
modules/i18n.py
---------------
Internationalization: Russian (primary) and Kazakh translations.
Usage:
    from modules.i18n import t
    t("overview.title")
"""
import streamlit as st

TRANSLATIONS = {
    "ru": {
        # Navigation
        "nav.overview":   "Обзор",
        "nav.training":   "Обучение моделей",
        "nav.comparison": "Сравнение моделей",
        "nav.predict":    "Анализ транзакции",
        "nav.external":   "Внешний банк",
        "nav.subtitle":   "Платформа антифрода",

        # Overview
        "overview.title":   "Обзор платформы",
        "overview.caption": "Сводка по всем обученным моделям на каждом датасете",
        "overview.no_metrics": "Метрики не найдены. Перейдите в раздел «Обучение» и запустите обучение.",
        "overview.dataset": "Датасет",
        "overview.roc_auc": "ROC-AUC",
        "overview.recall":  "Точность обнар.",
        "overview.precision": "Точность",
        "overview.f1":      "F1-оценка",
        "overview.tip":     "Ключевой показатель антифрода — **Recall по классу Fraud**: чем выше, тем меньше мошеннических транзакций остаётся незамеченными. Баланс с Precision минимизирует ложные срабатывания.",

        # Training
        "training.title":   "Обучение моделей",
        "training.caption": "Запустите обучение трёх ML-моделей на всех доступных датасетах",
        "training.datasets": "Датасеты",
        "training.models_section": "Модели для обучения",
        "training.start_btn": "Запустить обучение",
        "training.log_title": "Лог обучения",
        "training.running":   "Обучение выполняется — это может занять несколько минут...",
        "training.done":      "Обучение успешно завершено!",
        "training.warning":   "Обучение завершено с предупреждениями. Модели могут быть сохранены.",
        "training.results":   "Последние результаты",
        "training.no_metrics":"Запустите обучение, чтобы увидеть результаты.",
        "training.col.model": "Модель",
        "training.col.prec":  "Precision",
        "training.col.rec":   "Recall",
        "training.col.f1":    "F1",
        "training.col.auc":   "ROC-AUC",
        "training.col.fraud_rec": "Recall (Fraud)",
        "training.col.fraud_prec": "Precision (Fraud)",
        "training.col.time":  "Время (с)",

        # Model descriptions
        "model.lr.name":  "Логистическая регрессия",
        "model.lr.desc":  "Линейная базовая модель. Быстро обучается, интерпретируема, хорошо работает при линейно разделимых данных. Использует SAGA-оптимизатор и StandardScaler для нормализации признаков. Балансировка классов через class_weight='balanced'.",
        "model.lr.pros":  "Высокая скорость, полная интерпретируемость, стабильность",
        "model.lr.cons":  "Не улавливает нелинейные зависимости, чувствительна к выбросам",
        "model.lr.use":   "Базовый бенчмарк, объяснение решений регулятору",

        "model.rf.name":  "Случайный лес",
        "model.rf.desc":  "Ансамбль из 200 деревьев решений с бэггингом. Устойчив к выбросам, автоматически выбирает важные признаки, не требует нормализации. Метод balanced_subsample обеспечивает баланс классов в каждом дереве.",
        "model.rf.pros":  "Устойчивость к выбросам, встроенный feature importance, параллельное обучение",
        "model.rf.cons":  "Большой объём памяти, медленнее XGBoost на больших данных",
        "model.rf.use":   "Когда нужна интерпретируемость важности признаков",

        "model.xgb.name": "XGBoost / LightGBM",
        "model.xgb.desc": "Градиентный бустинг на деревьях. Лучший результат на несбалансированных данных благодаря параметру scale_pos_weight. Использует hist-алгоритм для ускорения обучения. 300 деревьев с learning_rate=0.05.",
        "model.xgb.pros": "Лучшее качество, быстрое обучение, встроенная регуляризация",
        "model.xgb.cons": "Требует тонкой настройки гиперпараметров",
        "model.xgb.use":  "Основная боевая модель для продакшена",

        "model.pros":  "Преимущества",
        "model.cons":  "Ограничения",
        "model.usecase": "Применение",
        "model.hyperparams": "Гиперпараметры",

        # Comparison
        "comparison.title":   "Сравнение моделей",
        "comparison.caption": "Детальный анализ: Precision, Recall, F1, ROC-AUC, матрица ошибок",
        "comparison.dataset": "Датасет:",
        "comparison.tab.all": "Все метрики",
        "comparison.tab.fraud": "Фокус на Fraud",
        "comparison.tab.cm":   "Матрица ошибок",
        "comparison.tab.report": "Полный отчёт",
        "comparison.fraud.tip": "Пропущенный фрод (False Negative) обходится значительно дороже ложной тревоги. Целевой показатель — Fraud Recall > 0.85.",
        "comparison.scatter.title": "Fraud: Precision vs Recall",
        "comparison.model":   "Модель:",
        "comparison.train_time": "Время обучения",

        # Predict
        "predict.title":   "Анализ транзакции",
        "predict.caption": "Введите параметры транзакции и получите мгновенную оценку риска от каждой модели",
        "predict.no_models": "Обученные модели не найдены. Запустите обучение.",
        "predict.model_set": "Набор моделей:",
        "predict.method":    "Способ ввода:",
        "predict.method.manual": "Ввод вручную",
        "predict.method.csv":    "Загрузить CSV",
        "predict.features": "Обнаружено признаков",
        "predict.btn":      "Анализировать",
        "predict.btn.all":  "Анализировать всё",
        "predict.results":  "Результаты анализа",
        "predict.avg_risk": "Средний риск",
        "predict.fraud":    "МОШЕННИЧЕСТВО",
        "predict.legit":    "ЛЕГИТИМНАЯ",
        "predict.high_risk":  "ВЫСОКИЙ РИСК — Транзакция с высокой вероятностью мошенническая. Требуется немедленная блокировка.",
        "predict.mid_risk":   "СРЕДНИЙ РИСК — Подозрительная транзакция. Рекомендуется ручная проверка.",
        "predict.low_risk":   "НИЗКИЙ РИСК — Транзакция выглядит легитимной.",
        "predict.total":      "Всего",
        "predict.flagged":    "Подозрительных",
        "predict.fraud_rate": "Доля фрода",
        "predict.showing":    "Показано 30 из",
        "predict.rest_zero":  "признаков. Остальные приравнены к 0.",

        # External
        "external.title":   "Внешний банк",
        "external.caption": "Приём и анализ транзакций от партнёрского банка с контекстными сигналами риска",
        "external.formula": "Формула риска",
        "external.tab.manual": "JSON вручную",
        "external.tab.csv":    "Загрузить CSV",
        "external.tab.api":    "API документация",
        "external.tab.history": "История",
        "external.score_btn":  "Проанализировать",
        "external.score_all":  "Анализировать всё",
        "external.no_history": "История пуста. Используйте другие вкладки для анализа транзакций.",
        "external.total":      "Транзакций",
        "external.flagged":    "Подозрительных",
        "external.fraud_rate": "Доля фрода",
        "external.risk_signals": "Сигналы риска:",
        "external.ml_prob":    "ML вероятность",
        "external.ctx_score":  "Контекст. риск",
        "external.combined":   "Итоговый риск",

        # Common
        "common.no_metrics": "Нет данных",
        "common.model": "Модель",
        "common.dataset": "Датасет",
        "common.fraud": "Мошенничество",
        "common.legit": "Легитимная",
        "common.predicted": "Предсказано",
        "common.actual": "Фактически",
        "common.seconds": "секунд",
    },

    "kz": {
        # Navigation
        "nav.overview":   "Шолу",
        "nav.training":   "Үлгілерді оқыту",
        "nav.comparison": "Үлгілерді салыстыру",
        "nav.predict":    "Транзакцияны талдау",
        "nav.external":   "Сыртқы банк",
        "nav.subtitle":   "Алаяқтыққа қарсы платформа",

        # Overview
        "overview.title":   "Платформаға шолу",
        "overview.caption": "Барлық датасеттердегі барлық оқытылған үлгілердің жиынтығы",
        "overview.no_metrics": "Метрика табылмады. «Оқыту» бөліміне өтіп, оқытуды іске қосыңыз.",
        "overview.dataset": "Датасет",
        "overview.roc_auc": "ROC-AUC",
        "overview.recall":  "Анықтау дәлдігі",
        "overview.precision": "Нақтылық",
        "overview.f1":      "F1-баға",
        "overview.tip":     "Алаяқтыққа қарсы күрестің негізгі көрсеткіші — **Fraud Recall**: жоғары болған сайын, азырақ алаяқтық транзакция байқалмай қалады.",

        # Training
        "training.title":   "Үлгілерді оқыту",
        "training.caption": "Барлық датасеттерде үш ML-үлгісін оқытыңыз",
        "training.datasets": "Датасеттер",
        "training.models_section": "Оқытылатын үлгілер",
        "training.start_btn": "Оқытуды бастау",
        "training.log_title": "Оқыту журналы",
        "training.running":   "Оқыту жүріп жатыр — бірнеше минут кетуі мүмкін...",
        "training.done":      "Оқыту сәтті аяқталды!",
        "training.warning":   "Оқыту ескертулермен аяқталды. Үлгілер сақталған болуы мүмкін.",
        "training.results":   "Соңғы нәтижелер",
        "training.no_metrics":"Нәтижелерді көру үшін оқытуды іске қосыңыз.",
        "training.col.model": "Үлгі",
        "training.col.prec":  "Precision",
        "training.col.rec":   "Recall",
        "training.col.f1":    "F1",
        "training.col.auc":   "ROC-AUC",
        "training.col.fraud_rec": "Recall (Fraud)",
        "training.col.fraud_prec": "Precision (Fraud)",
        "training.col.time":  "Уақыт (с)",

        # Model descriptions
        "model.lr.name":  "Логистикалық регрессия",
        "model.lr.desc":  "Сызықтық базалық үлгі. Жылдам оқытылады, түсіндіруге болады, сызықтық бөлінетін деректерде жақсы жұмыс жасайды.",
        "model.lr.pros":  "Жоғары жылдамдық, толық түсіндірімділік, тұрақтылық",
        "model.lr.cons":  "Сызықтық емес тәуелділіктерді қамтымайды",
        "model.lr.use":   "Базалық эталон, реттеушіге шешімдерді түсіндіру",

        "model.rf.name":  "Кездейсоқ орман",
        "model.rf.desc":  "200 шешім ағашының ансамблі. Аномалияларға төзімді, ерекшеліктердің маңыздылығын автоматты таңдайды.",
        "model.rf.pros":  "Аномалияларға төзімділік, ерекшеліктер маңыздылығы, параллель оқыту",
        "model.rf.cons":  "Үлкен жад көлемі, XGBoost-тан баяу",
        "model.rf.use":   "Ерекшеліктер маңыздылығын түсіндіру қажет болғанда",

        "model.xgb.name": "XGBoost / LightGBM",
        "model.xgb.desc": "Ағаштардағы градиенттік бустинг. Теңгерімсіз деректерде scale_pos_weight арқылы үздік нәтиже.",
        "model.xgb.pros": "Үздік сапа, жылдам оқыту, кіріктірілген реттеу",
        "model.xgb.cons": "Гиперпараметрлерді мұқият баптауды қажет етеді",
        "model.xgb.use":  "Өндірістегі негізгі модель",

        "model.pros":  "Артықшылықтары",
        "model.cons":  "Шектеулері",
        "model.usecase": "Қолдану",
        "model.hyperparams": "Гиперпараметрлер",

        # Comparison
        "comparison.title":   "Үлгілерді салыстыру",
        "comparison.caption": "Толық талдау: Precision, Recall, F1, ROC-AUC, қате матрицасы",
        "comparison.dataset": "Датасет:",
        "comparison.tab.all": "Барлық метрикалар",
        "comparison.tab.fraud": "Fraud фокусы",
        "comparison.tab.cm":   "Қате матрицасы",
        "comparison.tab.report": "Толық есеп",
        "comparison.fraud.tip": "Жіберілген алаяқтық (False Negative) жалған дабылдан әлдеқайда қымбатқа түседі. Мақсатты көрсеткіш — Fraud Recall > 0.85.",
        "comparison.scatter.title": "Fraud: Precision vs Recall",
        "comparison.model":   "Үлгі:",
        "comparison.train_time": "Оқыту уақыты",

        # Predict
        "predict.title":   "Транзакцияны талдау",
        "predict.caption": "Транзакция параметрлерін енгізіп, әрбір үлгіден жедел тәуекел бағасын алыңыз",
        "predict.no_models": "Оқытылған үлгілер табылмады. Оқытуды іске қосыңыз.",
        "predict.model_set": "Үлгілер жиыны:",
        "predict.method":    "Енгізу тәсілі:",
        "predict.method.manual": "Қолмен енгізу",
        "predict.method.csv":    "CSV жүктеу",
        "predict.features": "Анықталған белгілер",
        "predict.btn":      "Талдау",
        "predict.btn.all":  "Барлығын талдау",
        "predict.results":  "Талдау нәтижелері",
        "predict.avg_risk": "Орташа тәуекел",
        "predict.fraud":    "АЛАЯҚТЫҚ",
        "predict.legit":    "ЗАҢДЫ",
        "predict.high_risk":  "ЖОҒАРЫ ТӘУЕКЕЛ — Транзакция жоғары ықтималдылықпен алаяқтық. Жедел блокировка қажет.",
        "predict.mid_risk":   "ОРТАША ТӘУЕКЕЛ — Күмәнді транзакция. Қолмен тексеру ұсынылады.",
        "predict.low_risk":   "ТӨМЕН ТӘУЕКЕЛ — Транзакция заңды болып көрінеді.",
        "predict.total":      "Барлығы",
        "predict.flagged":    "Күмәнділер",
        "predict.fraud_rate": "Алаяқтық үлесі",
        "predict.showing":    "Көрсетілген 30 / ",
        "predict.rest_zero":  "белгі. Қалғандары 0-ге тең.",

        # External
        "external.title":   "Сыртқы банк",
        "external.caption": "Серіктес банктен транзакцияларды қабылдау және контекстік тәуекел сигналдарымен талдау",
        "external.formula": "Тәуекел формуласы",
        "external.tab.manual": "JSON қолмен",
        "external.tab.csv":    "CSV жүктеу",
        "external.tab.api":    "API құжаттамасы",
        "external.tab.history": "Тарих",
        "external.score_btn":  "Талдау",
        "external.score_all":  "Барлығын талдау",
        "external.no_history": "Тарих бос. Транзакцияларды талдау үшін басқа қойындыларды пайдаланыңыз.",
        "external.total":      "Транзакциялар",
        "external.flagged":    "Күмәнділер",
        "external.fraud_rate": "Алаяқтық үлесі",
        "external.risk_signals": "Тәуекел сигналдары:",
        "external.ml_prob":    "ML ықтималдылығы",
        "external.ctx_score":  "Контекст тәуекелі",
        "external.combined":   "Жалпы тәуекел",

        # Common
        "common.no_metrics": "Деректер жоқ",
        "common.model": "Үлгі",
        "common.dataset": "Датасет",
        "common.fraud": "Алаяқтық",
        "common.legit": "Заңды",
        "common.predicted": "Болжалды",
        "common.actual": "Нақты",
        "common.seconds": "секунд",
    }
}


def t(key: str) -> str:
    """Get translation for current language."""
    lang = st.session_state.get("lang", "ru")
    return TRANSLATIONS.get(lang, TRANSLATIONS["ru"]).get(key, key)


def lang_switch():
    """Render language switcher button in sidebar."""
    lang = st.session_state.get("lang", "ru")
    other = "kz" if lang == "ru" else "ru"
    label = "🇰🇿 Қазақша" if lang == "ru" else "🇷🇺 Русский"
    if st.button(label, key="lang_btn", use_container_width=False):
        st.session_state.lang = other
        st.rerun()
