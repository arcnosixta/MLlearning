import java.util.*;
public class Main {
    public static void main(String[] args) {
        Map<String, Integer> frequencies = new TreeMap<>();
        for (String word : List.of("java", "sql", "java")) frequencies.merge(word, 1, Integer::sum);
        System.out.println(frequencies);
        Deque<String> queue = new ArrayDeque<>();
        queue.offer("first");
        queue.offer("second");
        System.out.println(queue.poll());
        System.out.println(queue.poll());
    }
}
