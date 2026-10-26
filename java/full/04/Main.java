public class Main {
    static int lowerBound(int[] values, int key) {
        int left = 0, right = values.length;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (values[mid] < key) left = mid + 1;
            else right = mid;
        }
        return left;
    }
    public static void main(String[] args) {
        int[] values = {1, 2, 2, 5};
        System.out.println(lowerBound(values, 2));
        System.out.println(lowerBound(values, 9));
        System.out.println(lowerBound(new int[0], 1));
    }
}
