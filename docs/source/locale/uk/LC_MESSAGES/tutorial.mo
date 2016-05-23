��    5      �              l  �   m  A   �  =   1  F   o  1   �  ?   �  :   (  8   c  �   �     W     k  G   �     �  G   �  '   +     S  a   i     �     �  N   �  �   :  G   	  &   T	  +   {	  '   �	  �   �	  .   �
  N   �
     #     9  2   L  q     k   �  5   ]     �     �     �  �   �  �   �  }   3     �     �  �   �  ?   �  p   �     =  K   \  	   �     �     �  �   �     g    �  �   �  �   @  �   �  q   a  P   �  j   $  ]   �  b   �  )  P  %   z  5   �  �   �  #   k  f   �  9   �  2   0  z   c  !   �  #      �   $  ^  �  C     9   ]  B   �  @   �      J      �   k  (   �  '      n   >   �   �   �   y!  f   '"  -   �"     �"  1   �"    �"  %  $     <%  ;   =&  =   y&  6  �&  j   �'  �   Y(  :   $)  �   _)  &   �)  *   *  (   G*  �   p*  ;   a+   **Essential contract terms** can be modified by the submission of a new :ref:`change` object to the `Contract.changes` container. *Brokers (eMalls) can't create contracts in the contract system.* *Contract id is the same in both tender and contract system.* All `changes` are processed by the endpoint `/contracts/{id}/changes`. All changes are also listed on the contract view. And again we can confirm that there are two documents uploaded. And we can see that it is overriding the original version: Any future modification to the contract are not allowed. Before contract can be completed ``amountPaid`` field value should be set. Contract can be completed by switching to ``terminated`` status. Let's perform these actions in single request: Completing contract Contract in the tender system Contract is transferred from the tender system by an automated process. Creating contract Document can be added only while `change` is in the ``pending`` status. Document has to be added in two stages: Exploring basic rules Fields that can be modified: `title`, `description`, `status`, `value.amount`, `period`, `items`. Getting access Getting contract In case we made an error, we can reupload the document over the older version: In order to get rights for future contract editing, you need to use this view ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}`` with the API key of the eMall (broker), where tender was generated. In the ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}``: Just invoking it reveals an empty set. Let's access the URL of the created object: Let's add new `change` to the contract: Let's say that we have conducted tender and it has ``complete`` status. When the tender is completed,  contract (that has been created in the tender system) is transferred to the contract system **automatically**. Let's try exploring the `/contracts` endpoint: Let's update contract by supplementing it with all other essential properties. Let's view contracts. Modifying contract Note that contract is created in ``draft`` status. Procuring entity can upload PDF files into the created contract. Uploading should follow the :ref:`upload` rules. Response will contain ``access.token`` for the contract that can be used for further contract modification. See examples of `items` customization below. You can: Submitting contract change Tutorial Uploading documentation We do see the internal `id` of a contract (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/contracts/`) and its `dateModified` datestamp. We see the added properties have merged with existing contract data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp. You can make changes to the contract in cases described in the 4th part of Article 36 of the Law "On the Public Procurement". You can view all changes: You can view the `change`: `201 Created` response code and `Location` header confirm document creation. We can additionally query the `documents` collection API endpoint to confirm the action: `Change` can be modified while it is in the ``pending`` status: `Change` has to be applied by switching to the ``active`` status. After this `change` can't be modified anymore. ``id`` stands for contract id, ``tender_token`` is tender's token (is used for contract token generation). add item: delete item: update item: you should set document properties ``"documentOf": "change"`` and ``"relatedItem": "{change.id}"`` in order to bind the uploaded document to the `change`: you should upload document Project-Id-Version: openprocurement.contracting.api 1.0
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2016-04-25 17:22+0300
PO-Revision-Date: 2016-05-23 10:15+0300
Last-Translator: Zoriana Zaiats <sorenabell@quintagroup.com>
Language: uk
Language-Team: Ukrainian <support@quintagroup.com>
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.3.4
 **Істотні умови договору** можуть бути змінені поданням нового об’єкта :ref:`change` в котейнер `Contract.changes`. *Майданчики (брокери) не мають можливості створювати договори в системі договорів.* *Ідентифікатор `id` договору однаковий в системах закіпівель та договорів.* Всі зміни `change` обробляються точкою входу (endpoint) `/contracts/{id}/changes`. Всі зміни присутні при перегляді контракту. І знову можна перевірити, що є два завантажених документа. І ми бачимо, що вона перекриває оригінальну версію: Після цього додання змін до договору не дозволяється. Перед завершенням договору необхідно встановити значення поля  ``amountPaid``. Договір можна завершити переключенням у статус ``terminated``. Виконаємо ці дії єдиним запитом: Завершення договору Договір в системі закупівель Перенесенням договору із системи закупівель займається автоматизований процес. Створення договору Документ можна додати доки зміна `change` має статус ``pending``. Документ додається в два етапи: Розглянемо основні правила Поля, які можна модифікувати: `title`, `description`, `status`, `value.amount`, `period`, `items`. Отримання доступу Отримання договору Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії: Для того, щоб отримати права для майбутнього редагування договору, необхідно використати таку в’юшку ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}`` з API ключем майданчика, де була згенерована закупівля. В ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}``: При виклику видає пустий набір. Використаємо URL створеного об’єкта: Додамо нову зміну `change` до договору: Нехай у нас відбулась закупівля і вона є в статусі  ``complete``. Після цього договір, створений в системі закупівель, потрапляє в систему договорів. Подивимось як працює точка входу `/contracts`: Оновимо договір шляхом надання йому усіх інших важливих властивостей. Переглянемо договори. Редагування договору Зверніть увагу на те, що договір створюється у статусі ``draft``. Замовник може завантажити PDF файл у створений договір. Завантаження повинно відбуватись згідно правил :ref:`upload`. У відповіді буде ``access.token`` для договору, який буде використовуватись для модифікації договору. Дивіться приклади зміни елемента (`items`) нижче. Ви можете: Подання змін до договору Туторіал Завантаження документації Ми бачимо внутрішнє `id` договору (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/contracts/`) та його dateModified дату. Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації. Внесення змін до істотних умов договору можливі у випадках, описаних частиною четвертою статті 36 Закону України “Про публічні закупівлі”. Ви можете переглянути всі зміни: Ви можете переглянути зміну `change`: Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції документів, щоб підтвердити дію: Зміну `change` можна модифікувати доки вона має статус ``pending``. Зміна `change` буде застосована при переключенні в статус ``active``. ПІсля цього модифікувати зміну `change` вже не можна. ``id`` - це ідентифікатор договору, ``tender_token`` - це токен закупівлі (використовується для генерування токена договору). додати елемент (`items`): видалити елемент (`items`): оновити елемент (`items`): ви повинні задати властивості документа: ``"documentOf": "change"`` та ``"relatedItem": "{change.id}"``, щоб "прив’язати" завантажений документ до зміни `change`: ви повинні завантажити документ 