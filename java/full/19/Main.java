import java.util.concurrent.*;
public class Main {
    public static void main(String[] args) throws InterruptedException, ExecutionException {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        try {
            Future<Integer> first = pool.submit(() -> 20 + 1);
            Future<Integer> second = pool.submit(() -> 7 * 3);
            System.out.println(first.get());
            System.out.println(second.get());
        } finally {
            pool.shutdown();
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) pool.shutdownNow();
        }
    }
}
