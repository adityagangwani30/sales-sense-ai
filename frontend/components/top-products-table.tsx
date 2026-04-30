import type { TopProduct } from '@/lib/dashboard-types'
import { formatCurrency, formatNumber } from '@/lib/formatters'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface TopProductsTableProps {
  products: TopProduct[]
}

export function TopProductsTable({ products }: TopProductsTableProps) {
  return (
    <section className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-lg hover:bg-white/[7%] transition-colors">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white">Product Revenue</h2>
        <p className="text-sm text-gray-400 mt-1">
          Top performing products by revenue and order count.
        </p>
      </div>

      <Table>
        <TableHeader>
          <TableRow className="border-white/10 hover:bg-transparent">
            <TableHead className="font-semibold text-gray-400">Product</TableHead>
            <TableHead className="text-right font-semibold text-gray-400">Orders</TableHead>
            <TableHead className="text-right font-semibold text-gray-400">Revenue</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {products.slice(0, 8).map((product) => (
            <TableRow key={product.product_name} className="hover:bg-white/[3%] border-white/5">
              <TableCell className="max-w-[260px] text-wrap font-medium text-white py-3">
                {product.product_name}
              </TableCell>
              <TableCell className="text-right text-gray-400 py-3">
                {formatNumber(product.order_count)}
              </TableCell>
              <TableCell className="text-right font-semibold text-white py-3">
                {formatCurrency(product.total_revenue)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </section>
  )
}
