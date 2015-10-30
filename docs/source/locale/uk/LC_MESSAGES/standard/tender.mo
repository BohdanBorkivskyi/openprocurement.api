��    K      t  e   �      `     a          �     �     �     G  2   g     �     �     �     �  6   �     (  C   C     �     �     �     �     �  /   �     /	     O	     l	  $   �	      �	     �	     �	     	
  .   )
  .   X
  #   �
  !   �
  I   �
  I     5   a     �     �     �     �     �  s   �  &   k  :   �  S   �  B   !  L   d  "   �  $   �  2   �  C   ,     p     �     �     �  ]   �     0     D  %   c  3   �     �     �      �     �  9   
     D  U   H  F   �  �   �  Q   l  �   �  �   K  U   �  ~   L  ?   �  �    ,     .   1  &   `  %   �    �  ?   �  Z        ]  .   l  X   �  :   �  M   /  :   }  �   �  2   D     w  .   �  2   �  *   �  H     .   e  +   �  )   �  3   �  /     .   N  *   }  .   �  ]   �  V   5  C   �  =   �  �     �   �  J   '  
   r  @   }      �     �  @   �  �   '   M   �   k   *!  �   �!  �   "  �   �"  D   @#  F   �#  Y   �#  �   &$     �$     �$     �$     �$  �   %  /   �%  -   �%  C   &  ]   P&     �&  
   �&  Y   �&  $   1'  l   V'     �'  �   �'  n   Z(  �   �(  v   �)  �   *  (  �*  �   ,  �   �,  \   }-        9   >                    -   ?   +       2   	          C       1   !   I   %             @       $      8             7       F                 4   6   3      .   /          E          J          '   H              (         G               *   <   &             5          B                                     =   ;       ,   0   D   K   A   #   )       "   
   :    :ref:`organization`, required :ref:`period`, read-only :ref:`period`, required :ref:`value`, required A list of all bids placed in the tender with information about tenderers, their proposal and other qualification documentation. A web address for view auction. All qualifications (disqualifications and awards). Auction Auction period (auction) Awarding process period. Cancelled tender (cancelled) Complaints to tender conditions and their resolutions. Complete tender (complete) Contains 1 object with `active` status in case of cancelled Tender. Contains all tender lots. Current time Detailed description of tender. Enquiries period (enquiries) Features of tender. Historical changes to Tender object properties. List of :ref:`Contract` objects List of :ref:`award` objects List of :ref:`bid` objects List of :ref:`cancellation` objects. List of :ref:`complaint` objects List of :ref:`document` objects List of :ref:`lot` objects. List of :ref:`question` objects List of :ref:`revision` objects, autogenerated List that contains single item being procured. Organization conducting the tender. Period when Auction is conducted. Period when bids can be submitted. At least `endDate` has to be provided. Period when questions are allowed. At least `endDate` has to be provided. Questions to ``procuringEntity`` and answers to them. Schema Standstill period (standstill) Status of the Tender. Tender Tendering period (tendering) The :ref:`cancellation` object describes the reason of tender cancellation contains accompanying documents  if any. The Tender dates should be sequential: The minimal step of auction (reduction). Validation rules: The name of the tender, displayed in listings. You can include the following items: The tender identifier to refer tender to in "paper" documentation. Total available tender budget. Bids greater then ``value`` will be rejected. Unsuccessful tender (unsuccessful) Winner qualification (qualification) `amount` should be less then `Tender.value.amount` `currency` should either be absent or match `Tender.value.currency` `enquiryPeriod.endDate` `enquiryPeriod.startDate` `tenderPeriod.endDate` `tenderPeriod.startDate` `valueAddedTaxIncluded` should either be absent or match `Tender.value.valueAddedTaxIncluded` item being procured list of :ref:`Feature` objects list of :ref:`item` objects, required periodicity of the tender (annual, quarterly, etc.) some other info string string, autogenerated, read-only string, multilingual tender code (in procuring organization management system) url |ocdsDescription| A list of all the companies who entered submissions for the tender. |ocdsDescription| All documents and attachments related to the tender. |ocdsDescription| TenderID should always be the same as the OCID. It is included to make the flattened data structure more convenient. |ocdsDescription| The date or period on which an award is anticipated to be made. |ocdsDescription| The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured. |ocdsDescription| The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead. |ocdsDescription| The period during which enquiries may be made and will be answered. |ocdsDescription| The period when the tender is open for submissions. The end date is the closing date for tender submissions. |ocdsDescription| The total estimated value of the procurement. Project-Id-Version: openprocurement.api 0.10
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2014-11-24 18:25+0200
PO-Revision-Date: 2015-10-30 17:13+0200
Last-Translator: Zoriana Zaiats <sorenabell@quintagroup.com>
Language-Team: Ukrainian <info@quintagroup.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Language: uk
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
X-Generator: Poedit 1.8.5
 :ref:`organization`, обов’язково :ref:`period`,  лише для читання :ref:`period`, обов’язково :ref:`value`, обов’язково Список усіх пропозицій зроблених під час закупівлі разом з інформацією про учасників закупівлі, їхні пропозиції та інша кваліфікаційна документація. Веб-адреса для перегляду аукціону. Усі  кваліфікації (дискваліфікації та переможці). Аукціон Період аукціону (аукціон) Період, коли відбувається визначення переможця. Відмінена закупівля (відмінена) Скарги на умови закупівлі та їх вирішення. Завершена закупівля (завершена) Містить 1 об’єкт зі статусом `active` на випадок, якщо Закупівлю буде відмінено. Містить всі лоти закупівлі. Поточний час Детальний опис закупівлі Період уточнень (уточнення) Властивості закупівлі. Зміни властивостей об’єктів Закупівлі Список об’єктів :ref:`Contract` Список об’єктів :ref:`award` Список об’єктів :ref:`bid` Список об’єктів :ref:`cancellation`. Список об’єктів :ref:`complaint` Список об’єктів :ref:`document` Список об’єктів :ref:`lot`. Список об’єктів :ref:`question` Список об’єктів :ref:`revision`, генерується автоматично Список, який містить елемент, що закуповується. Організація, що проводить закупівлю. Період, коли проводиться аукціон. Період, коли подаються пропозиції. Повинна бути вказана хоча б `endDate` дата. Період, коли дозволено задавати питання. Повинна бути вказана хоча б `endDate` дата. Питання до ``procuringEntity`` і відповіді на них. Схема Пропозиції розглянуто (розглянуто) Статус Закупівлі. Tender Очікування пропозицій (пропозиції) Об’єкт :ref:`cancellation` описує причину скасування закупівлі та надає відповідні документи, якщо такі є. Дати закупівлі повинні бути послідовними: Мінімальний крок аукціону (редукціону). Правила валідації: Назва тендера, яка відображається у списках. Можна включити такі елементи: Ідентифікатор закупівлі, щоб знайти закупівлю у  "паперовій" документації Повний доступний бюджет закупівлі. Пропозиції, що більші за ``value`` будуть відхилені. Закупівля не відбулась (не відбулась) Кваліфікація переможця (кваліфікація) Значення `amount` повинно бути меншим за `Tender.value.amount` Значення `currency` повинно бути або відсутнім, або співпадати з `Tender.value.currency` `enquiryPeriod.endDate` `enquiryPeriod.startDate` `tenderPeriod.endDate` `tenderPeriod.startDate` Значення `valueAddedTaxIncluded` повинно бути або відсутнім, або співпадати з `Tender.value.valueAddedTaxIncluded` елемент, що закуповується список об’єктів :ref:`Feature` список об’єктів :ref:`item`, обов’язково періодичність закупівлі (щороку, щокварталу, і т.д.) інша інформація рядок рядок, генерується автоматично, лише для читання рядок, багатомовний код закупівлі (у системі управління організації-замовника) URL-адреса |ocdsDescription| Список усіх компаній, які подали заявки для участі у закупівлі. |ocdsDescription| Всі документи та додатки пов’язані із закупівлею. |ocdsDescription| TenderID повинен завжди співпадати з OCID. Його включають, щоб зробити структуру даних більш зручною. |ocdsDescription| Дата або період, коли очікується визначення переможця. |ocdsDescription| Об’єкт, що управляє закупівлею. Він не обов’язково є покупцем, який платить / використовує закуплені елементи. |ocdsDescription| Товари та послуги, що будуть закуплені, поділені на спискові елементи, де це можливо. Елементи не повинні дублюватись, замість цього вкажіть кількість 2. |ocdsDescription| Період, коли можна зробити уточнення та отримати відповіді на них. |ocdsDescription| Період, коли закупівля відкрита для подачі пропозицій. Кінцева дата - це дата, коли перестають прийматись пропозиції. |ocdsDescription| Загальна кошторисна вартість закупівлі. 