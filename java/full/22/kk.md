# XML: DOM, SAX, StAX, XPath және XSD

Мақсат: XML моделін таңдап, құрылымды тексеру және сыртқы ресурстарды басқару.

## XML модельдері

Well-formed құжат синтаксисі дұрыс, valid құжат схемаға сәйкес. Namespace URI кеңістікті анықтайды, префикс өзгеретін қысқарту ғана. XSD тип, рет, міндеттілік және мән шегін анықтайды. DTD — бөлек ескі құрылым механизмі.

DOM бүкіл ағашты жадқа жүктейді; өзгертуге ыңғайлы. getElementsByTagName барлық ұрпақты іздейді. XPath түйіндерді таңдайды; namespace үшін контекст қажет. XML жазуға Transformer қолдан, мәтінді экрандамай біріктірме.

SAX оқиғаларды өзі жібереді, StAX оқиғасын бағдарлама сұрайды. characters бір элементке бірнеше рет келуі мүмкін, мәтінді жина. Үлкен құжат үшін ағындық модель жадты үнемдейді.

SchemaFactory және Validator XSD тексереді. ACCESS_EXTERNAL_DTD/SCHEMA арқылы сыртқы қолжетімділікті шекте. DOCTYPE саясатын анықта: бір expandEntityReferences баптауы жеткіліксіз. JAXB Java 17 JDK құрамына кірмейді, JAXP java.xml кіреді.

## Мысал

{{example}}

## Практика

### 1. XSD

Міндетті id және 0–100 бағасы бар student схемасын жаса.

{{answer:1}}

<details><summary>Шешім</summary>

use="required", xs:int шектеулері minInclusive/maxInclusive. id жоқ және 101 бар құжатты Validator қабылдамауы тиіс.
</details>

### 2. SAX мәтіні

characters екі рет келсе не істейсің?

{{answer:2}}

<details><summary>Шешім</summary>

startElement кезінде StringBuilder баста, әр бөлікті offset/length арқылы қос, endElement кезінде қолдан.
</details>

### 3. Үлкен файл

Миллион student санауға модель таңда.

{{answer:3}}

<details><summary>Шешім және тексеру</summary>

SAX не StAX санауышы жеткілікті. DOM барлық түйінді сақтар еді. Well-formed пен valid айырмасы қандай?
</details>
