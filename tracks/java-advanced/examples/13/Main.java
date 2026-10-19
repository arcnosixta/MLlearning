public class Main {static class Stock {private int available=5;synchronized boolean reserve(int n){if(n<=0||n>available)return false;available-=n;return true;}synchronized int left(){return available;}}
public static void main(String[] args){var stock=new Stock();System.out.println(stock.reserve(3));System.out.println(stock.reserve(3));System.out.println(stock.left());}}
