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
    <section className="rounded-2xl border border-border/70 bg-card/90 p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-foreground">Product Revenue Table</h2>
        <p className="text-sm text-foreground/60">
          Exact values behind the ranked product performance chart.
        </p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Product</TableHead>
            <TableHead className="text-right">Orders</TableHead>
            <TableHead className="text-right">Revenue</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {products.slice(0, 8).map((product) => (
            <TableRow key={product.product_name}>
              <TableCell className="max-w-[260px] text-wrap font-medium text-foreground">
                {product.product_name}
              </TableCell>
              <TableCell className="text-right text-foreground/70">
                {formatNumber(product.order_count)}
              </TableCell>
              <TableCell className="text-right font-semibold text-foreground">
                {formatCurrency(product.total_revenue)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </section>
  )
}
