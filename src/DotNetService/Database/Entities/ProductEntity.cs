﻿namespace Orders.Database.Entities
{
    public class ProductEntity
    {
        public int Id { get; set; }
        public int OrderId { get; set; }
        public int ProductId { get; set; }
        public decimal Quantity { get; set; }
        public decimal SoldPrice { get; set; }
    }
}