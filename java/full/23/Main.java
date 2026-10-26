import java.util.List;
public class Main {
    interface Component { int price(); }
    record Item(int price) implements Component {
        Item { if (price < 0) throw new IllegalArgumentException(); }
    }
    record Bundle(List<Component> children) implements Component {
        Bundle { children = List.copyOf(children); }
        public int price() { return children.stream().mapToInt(Component::price).sum(); }
    }
    public static void main(String[] args) {
        Component basket = new Bundle(List.of(new Item(10), new Bundle(List.of(new Item(20), new Item(5)))));
        System.out.println(basket.price());
    }
}
