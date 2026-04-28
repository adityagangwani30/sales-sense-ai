export interface SalesMetric {
  date: string;
  sales: number;
  transactions: number;
  avgOrderValue: number;
  conversionRate: number;
}

export interface ProductData {
  name: string;
  sales: number;
  revenue: number;
  growth: number;
}

export interface DepartmentData {
  department: string;
  sales: number;
  target: number;
  performance: number;
}

export interface HourlyData {
  time: string;
  sales: number;
  customers: number;
}

export const retailDataset: SalesMetric[] = [
  { date: 'Jan 1', sales: 4200, transactions: 240, avgOrderValue: 175, conversionRate: 8.2 },
  { date: 'Jan 2', sales: 3800, transactions: 221, avgOrderValue: 172, conversionRate: 7.9 },
  { date: 'Jan 3', sales: 5200, transactions: 290, avgOrderValue: 179, conversionRate: 9.1 },
  { date: 'Jan 4', sales: 4900, transactions: 270, avgOrderValue: 181, conversionRate: 8.8 },
  { date: 'Jan 5', sales: 6100, transactions: 330, avgOrderValue: 185, conversionRate: 10.2 },
  { date: 'Jan 6', sales: 5800, transactions: 310, avgOrderValue: 187, conversionRate: 9.7 },
  { date: 'Jan 7', sales: 7200, transactions: 380, avgOrderValue: 189, conversionRate: 11.5 },
];

const ecommerceDataset: SalesMetric[] = [
  { date: 'Jan 1', sales: 5200, transactions: 180, avgOrderValue: 289, conversionRate: 5.2 },
  { date: 'Jan 2', sales: 4800, transactions: 160, avgOrderValue: 300, conversionRate: 4.8 },
  { date: 'Jan 3', sales: 6200, transactions: 210, avgOrderValue: 295, conversionRate: 6.1 },
  { date: 'Jan 4', sales: 5900, transactions: 195, avgOrderValue: 302, conversionRate: 5.8 },
  { date: 'Jan 5', sales: 7100, transactions: 235, avgOrderValue: 302, conversionRate: 6.9 },
  { date: 'Jan 6', sales: 6800, transactions: 220, avgOrderValue: 309, conversionRate: 6.6 },
  { date: 'Jan 7', sales: 8200, transactions: 270, avgOrderValue: 304, conversionRate: 7.8 },
];

export function getDatasetByName(name: string): SalesMetric[] {
  return name === 'retail' ? retailDataset : ecommerceDataset;
}

export const productSales: ProductData[] = [
  { name: 'Electronics', sales: 12500, revenue: 425000, growth: 12.5 },
  { name: 'Apparel', sales: 9800, revenue: 320000, growth: 8.3 },
  { name: 'Home & Garden', sales: 7200, revenue: 215000, growth: 15.2 },
  { name: 'Beauty', sales: 5600, revenue: 180000, growth: 6.8 },
  { name: 'Sports', sales: 4300, revenue: 155000, growth: 4.2 },
];

export const departmentPerformance: DepartmentData[] = [
  { department: 'North Store', sales: 45200, target: 40000, performance: 113 },
  { department: 'South Store', sales: 38900, target: 40000, performance: 97 },
  { department: 'East Store', sales: 52100, target: 45000, performance: 116 },
  { department: 'West Store', sales: 41800, target: 42000, performance: 100 },
  { department: 'Downtown', sales: 35600, target: 38000, performance: 94 },
];

export const hourlyTraffic: HourlyData[] = [
  { time: '12 AM', sales: 240, customers: 42 },
  { time: '2 AM', sales: 180, customers: 28 },
  { time: '4 AM', sales: 120, customers: 18 },
  { time: '6 AM', sales: 320, customers: 52 },
  { time: '8 AM', sales: 640, customers: 105 },
  { time: '10 AM', sales: 1200, customers: 198 },
  { time: '12 PM', sales: 1800, customers: 295 },
  { time: '2 PM', sales: 1400, customers: 230 },
  { time: '4 PM', sales: 1600, customers: 260 },
  { time: '6 PM', sales: 2100, customers: 340 },
  { time: '8 PM', sales: 1900, customers: 310 },
  { time: '10 PM', sales: 900, customers: 145 },
];

export const kpiMetrics = {
  totalRevenue: '$2,847,300',
  totalTransactions: 15240,
  avgOrderValue: '$186.92',
  conversionRate: '8.5%',
  customerSatisfaction: '4.7/5',
  inventoryTurnover: '6.2x',
  repeatCustomerRate: '42%',
  revenueGrowth: '+12.8%',
};
