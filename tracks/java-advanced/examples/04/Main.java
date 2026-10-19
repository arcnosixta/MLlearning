import java.util.concurrent.*;
public class Main {
    public static void main(String[] args) throws Exception {
        ExecutorService pool=Executors.newFixedThreadPool(2);
        try {
            Future<Integer> a=pool.submit(()->20);
            Future<Integer> b=pool.submit(()->22);
            System.out.println(a.get(2,TimeUnit.SECONDS)+b.get(2,TimeUnit.SECONDS));
        } finally {
            pool.shutdown();
            if(!pool.awaitTermination(2,TimeUnit.SECONDS)) pool.shutdownNow();
        }
    }
}
