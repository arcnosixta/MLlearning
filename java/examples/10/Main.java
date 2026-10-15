import java.util.*;
public class Main {
    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("A", "B", "A"));
        Set<String> unique = new LinkedHashSet<>(names);
        Map<String,Integer> counts = new LinkedHashMap<>();
        for (String name : names) counts.merge(name, 1, Integer::sum);
        System.out.println(unique);
        System.out.println(counts);
    }
}
