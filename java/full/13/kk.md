# Generics, тип шектеулері және PECS

Мақсат: тип қателерін орындауға дейін анықтайтын ортақ код жазу.

## Типтер байланысы

Box<T> ішінде T нақты типпен ауыстырылады. Примитив орнына Integer сияқты орауыш қолданылады. Raw type тип қауіпсіздігін азайтады. Generic әдіс `<T>` параметрін нәтиже типінен бұрын жариялайды.

List<Integer> — List<Number> мұрагері емес: әйтпесе оған Double қосылар еді. `? extends Number` көзінен Number оқылады, нақты санды қосу қауіпсіз емес. `? super Integer` Integer қабылдайды, бірақ оқылған мән тек Object ретінде кепілденеді. PECS: өндірушіге extends, тұтынушыға super. Wildcard өзгермейтіндікке кепіл емес.

`T extends Number` қолжетімді әдістерді шектейді. Бірнеше bound ішінде класс бірінші тұрады. Тип параметрлері негізінен өшіріледі, сондықтан new T() және instanceof List<String> болмайды. Жасау үшін Supplier<T> бер. SuppressWarnings келісім қатесін түземейді.

## Мысал

{{example}}

## Практика

### 1. Бірінші элемент

Бос тізімге Optional.empty қайтаратын generic first жаз.

{{answer:1}}

<details><summary>Шешім</summary>

`<T> Optional<T> first(List<T> values)`; null-сыз тізімде of(values.get(0)) қолдан.
</details>

### 2. Қосынды

List<Integer> және List<Double> қабылда.

{{answer:2}}

<details><summary>Шешім</summary>

List<? extends Number> параметрін оқып, doubleValue қос. Жуық есептеу дәлдігін ескер.
</details>

### 3. Super

Неге super Integer-ден оқылған мән Integer болуға міндетті емес?

{{answer:3}}

<details><summary>Шешім және тексеру</summary>

Нақты тип List<Object> болуы мүмкін. Ол Integer қабылдайды, бірақ ішінде өзге Object бар. Wildcard пен T айырмасы қандай?
</details>
