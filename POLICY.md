# Політика синтетичного release-workflow v1

Домен — agentic coding: дозвіл merge в захищену гілку. Це локальна дослідницька політика, а не повна емуляція GitHub. Джерело доменних вимог: [GitHub, About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), перевірено 23.09.2026: required status checks, required reviews, dismiss stale approvals, approval by someone other than last pusher. Решта (повна version tuple, queue, TTL, retry) — явно задані дослідницькі розширення, не вимоги GitHub.

## Стан і записи

Кожна епізода незалежна. Початковий стан: commit=c1, base=b1, policy=p1, component=m1, input=i1, pusher=author; scope=true, eligible=true; budget=1; queue=0, capacity=1; review_required=true; review_ttl=10; deadline=20; failure=false. Немає CI, review request, approval чи rejection. t починається з 0. Час — умовні simulated ticks, не секунди.

JSON епізоди: `id`, `family`, `split`, `description`, `events`. Події мають `t` (невід'ємний, неспадний), `op` і наведені нижче поля. Ідентичність доказів: шість полів commit/base/policy/component/input/pusher. Кожна зміна хоча б одного поля скасовує CI, запит, approval і rejection, навіть якщо згодом поле повернулося до попереднього значення (захист ABA).

- `change`: одне або кілька полів із шістки. Лише фактична зміна інвалідує докази.
- `settings`: scope, eligible, review_required, queue, capacity, deadline, review_ttl; ненаведені не змінюються. Ці поля самі не скасовують записи; чинність обмежень перевіряється під час attempt.
- `ci`: `status` = pass/fail/unknown; результат для поточного стану. Останній запис замінює попередній. Це спільний ідеалізований детектор, а не вимір реального тестування.
- `failure`: `active` = true/false; false означає зафіксоване усунення відмови. Бюджет не поповнюється.
- `review`: `outcome` = approve/reject/revoke, `reviewer` = author або maintainer, `qualified` = true/false. Approve/reject приймається тільки якщо є поточний запит, qualified=true, reviewer != pusher, t <= deadline, t-request_time <= review_ttl. Revoke завжди скасовує approval і pending request, незалежно від інших полів (fail closed). Подія без чинних передумов ігнорується та реєструється invalid_review.
- `attempt`: оцінити дозвіл і записати рішення. Жодної реальної дії не виконується. Review request / simulated release / retry записується у журнал як описано нижче. Епізода може мати кілька attempts; оцінюється кожен.

## Рішення на attempt: порядок причин

1. scope=false → block/stop; eligible=false → block/switch. t > deadline → block/stop (expiry всієї дії, не тільки review).
2. CI != pass → block/verify (fail та unknown ніколи не pass).
3. failure=true → block/retry, якщо budget>0; при цьому витратити 1 budget. Інакше block/stop. Сам retry не усуває failure.
4. Чинний reject → block/stop (новий request за тією самою версією не скасовує reject).
5. review_required=false → allow/act. Інакше чинний approval (t-approval_time <= review_ttl) → allow/act. Вихід рецензента з черги не скасовує завершеного approval.
6. Без чинного approval потрібне review. Якщо capacity<=queue → review/defer (нуль capacity також означає недоступність); у цій гілці нового запиту НЕ створювати. Інакше review/escalate: якщо поточного не простроченого запиту немає — записати новий review_request з t; якщо є — не дублювати. Прострочення запиту: t-request_time > review_ttl. Queue — задане зовнішнє навантаження, а не кількість запитів цієї епізоди.

Кожен allow записує simulated release. Approval/reject при валідному прийомі завершує pending request; approval зберігає час прийому. Reject діє до change або revoke. При відсутності/простроченні approval старий approval не замінює нового request. Всі правила однакові для RAC і stateful baseline.

Мітки: allow/review/block; якщо задані факти не дозволяють оцінити — insufficient_information. Суддя позначає всі attempts і пояснює їх; не має бачити реалізації, авторські очікування або відповіді інших суддів. Це оцінювання правил синтетичного coding-workflow, не людська експертиза й не перевірка правдивості детекторів.
