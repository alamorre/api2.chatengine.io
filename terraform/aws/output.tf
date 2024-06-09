output "redis_host" {
  value = aws_elasticache_cluster.redis_cluster.cache_nodes[0].address
}

output "redis_port" {
  value = aws_elasticache_cluster.redis_cluster.port
}
