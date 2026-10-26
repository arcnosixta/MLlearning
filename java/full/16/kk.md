# Stream API, коллекторлар және Optional

Мақсат: деректерді жанама ортақ күйсіз конвейермен өңдеу.

## Конвейер ережелері

Stream — бір рет қолданылатын есептеу. filter, map, flatMap, sorted аралық сатылар, toList, collect, reduce, count терминалдық әрекеттер. Терминалдық әрекет болмай есептеу әдетте басталмайды. Бір stream-ді қайта қолданба. Шексіз көзге limit қажет.

map бір элементті бір мәнге өзгертеді, flatMap ішкі ағындарды жаяды. distinct equals/hashCode қолданады. peek ішіндегі міндетті әрекетке сенбе: оңтайландыру оны өткізуі мүмкін.

reduce амалы ассоциативті, бастапқы мәні бейтарап болуы керек. groupingBy топтайды, counting санайды, toMap дубликат кілт саясатын қажет етеді. Java 17 toList өзгермейтін тізім береді.

Optional бос нәтижені көрсетеді. map, orElseGet, orElseThrow қолдан. orElse аргументті алдын ала, orElseGet қажет кезде есептейді. parallel автоматты жылдамдатпайды; ортақ ArrayList-ке forEach арқылы қосу қауіпті. Files.lines ағынын жабу қажет.

## Мысал

{{example}}

## Практика

### 1. Сөздер

Сөйлемдерден бірегей сұрыпталған сөздер ал.

{{answer:1}}

<details><summary>Шешім</summary>

split, flatMap, босын filter, регистрді біріздендіру, distinct, sorted, toList тізбегін қолдан.
</details>

### 2. Топтар

Әр студент тобындағы адам санын тап.

{{answer:2}}

<details><summary>Шешім</summary>

groupingBy(Student::group, counting()). Рет керек болса TreeMap::new бер. Санау нәтижесі Long.
</details>

### 3. Бос орташа

Неліктен бос орташаға нөл қою әрдайым дұрыс емес?

{{answer:3}}

<details><summary>Шешім және тексеру</summary>

Нөл заңды орташа болуы мүмкін. OptionalDouble не «баға жоқ» күйін сақта. map пен flatMap айырмасы қандай? Азайту неге parallel reduce үшін жарамсыз?
</details>
