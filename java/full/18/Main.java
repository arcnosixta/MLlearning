public class Main {
    static final class Counter {
        private int value;
        synchronized void increment() { value++; }
        synchronized int get() { return value; }
    }
    public static void main(String[] args) throws InterruptedException {
        Counter counter = new Counter();
        Runnable task = () -> { for (int i = 0; i < 1000; i++) counter.increment(); };
        Thread first = new Thread(task);
        Thread second = new Thread(task);
        first.start();
        second.start();
        first.join();
        second.join();
        System.out.println(counter.get());
    }
}
