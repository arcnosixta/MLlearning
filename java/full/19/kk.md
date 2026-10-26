# Executors, Future және concurrency құралдары

Мақсат: тапсырма өмірін және параллелизм шегін басқару.

## Тапсырмалар

ExecutorService Runnable және Callable қабылдайды. submit Future қайтарады, get күтеді, ExecutionException қате себебін орайды. get таймауты есептеуді өзі тоқтатпайды. cancel(true) interrupt сұрайды. Java 17 ішінде пулды finally арқылы shutdown жаса; ол try-with-resources ресурсы емес.

Пулдың ағын саны, кезек көлемі және бас тарту саясаты жүктемені шектейді. FixedThreadPool кезегі шағын тұрақты лимитпен шектелмейді. ScheduledExecutorService fixedRate пен fixedDelay айырмасын сақтайды. ForkJoin есепті бөліктерге бөлуге ыңғайлы.

AtomicInteger бір жаңартуды атомарлы етеді. ReentrantLock-ты finally ішінде босат. Semaphore ресурс санын, CountDownLatch бір реттік күтуді, CyclicBarrier қайталама кездесуді басқарады. BlockingQueue өндіруші-тұтынушыға кері қысым береді.

ConcurrentHashMap ішінде merge/compute қолдан; get+put бір операция емес. CopyOnWriteArrayList жазуда көшірме жасайды. CompletableFuture thenApply мәнді өзгертеді, thenCompose ішкі future-ді біріктіреді. Блоктайтын жұмыстың executor-ын нақты таңда.

## Мысал

{{example}}

## Практика

### 1. Таймаут

Future нәтижесін бір секунд күт.

{{answer:1}}

<details><summary>Шешім</summary>

get(1,SECONDS), TimeoutException кезінде cancel(true). Прерывание флагын сақта.
</details>

### 2. Жиілік

Ортақ картада сөздерді сана.

{{answer:2}}

<details><summary>Шешім</summary>

ConcurrentHashMap.merge қолдан. Соңғы нәтижеге дейін барлық тапсырманы күт.
</details>

### 3. Кезек

Он элементтік буфер және аяқталу сигналын жаса.

{{answer:3}}

<details><summary>Шешім және тексеру</summary>

ArrayBlockingQueue(10), put/take және арнайы аяқталу хабарын қолдан. Өндіруші қатесінде де тұтынушы босқа күтпеуі тиіс. shutdown неге бірден тоқтатпайды?
</details>
