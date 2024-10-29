import uuid
from collections import deque

# Definindo a classe Ordem
class Order:
    def __init__(self, order_type, side, qty, price=None, pegged_to=None):
        self.id = str(uuid.uuid4()) # gera um identificador unico para a ordem
        self.type = order_type   # tipo da ordem
        self.side = side         # buy ou sell
        self.qty = qty           # quantidade
        self.price = price       # preço
        self.pegged_to = pegged_to # preço dinamico
 # Definindo a classe da Máquina que faz as trocas
        
class MatchingEngine:
    def __init__(self):
        self.buy_orders = deque()   # fila de ordens de compra
        self.sell_orders = deque()  # fila de ordens de venda
        self.pegged_orders = []     # fila de orden pegged
     
     # função para adicionar ordens nas respectivas filas, se for a mercado executa automaticamente  
    def add_order(self, order_type, side, qty, price=None, pegged_to=None):
        order = Order(order_type, side, qty, price, pegged_to)
        
        if pegged_to:
            self.pegged_orders.append(order)
            print(f"Pegged order created: {side} {qty} pegged to {pegged_to} {order.id}")
        elif order_type == "limit":
           self._add_limit_order(order, side)
        elif order_type == "market":
            self.execute_market_order(order)
            
        self.sort_orders()
        self.update_pegged_orders()
        
        # adiciona uma ordem limitada e tenta casar com uma ordem do lado oposto
    def _add_limit_order(self, order, side):
        if side == "buy":
            self.match_order(order, self.sell_orders)
            if order.qty > 0:
                self.buy_orders.append(order)
        else:
            self.match_order(order, self.buy_orders)
            if order.qty > 0:
                self.sell_orders.append(order)
        print(f"order created: {side} {order.qty} @ {order.price} {order.id}")        
     
     #  Executa uma ordem de mercado           
    def execute_market_order(self, order):
        if order.side == "buy":
            self.match_order(order, self.sell_orders)
        elif order.side == "sell":
            self.match_order(order, self.buy_orders)
    
    # casa ordens de lados opostos, se nao forem compativeis a ordem nao é preenchida        
    def match_order(self, market_order, limit_orders):
        total_qty_traded = 0 # quantidade total negociada
        price = None         # preço da negociaçao
        
        while market_order.qty > 0 and limit_orders:
            limit_order = limit_orders[0]
            
            if (market_order.side == "buy" and market_order.price < limit_order.price) or \
                (market_order.side == "sell" and market_order.price > limit_order.price):
                    print("Preço incompatível") # preço incompativel
                    return
            
            if price is None:
                price = limit_order.price # define o preço da negociaçao
                
                trade_qty = min(market_order.qty, limit_order.qty)
                total_qty_traded += trade_qty
                
                market_order.qty -= trade_qty
                limit_order.qty -= trade_qty
                
            if limit_order.qty == 0:
                limit_orders.popleft() # remove a ordem preenchida
                
        if total_qty_traded > 0:
            print(f"trade, price: {price}, qty: {total_qty_traded}")
      
    # Função para cancelar uma ordem      
    def cancel_order(self, order_id):
        print("\nVerificando ordens disponíveis para cancelamento:")
        for orders in [self.buy_orders, self.sell_orders, self.pegged_orders]:
            for order in orders:
                print(f"Ordem disponível - ID: {order.id}")

    # Verifica e remove a ordem com o ID especificado
                if order.id == order_id:
                    orders.remove(order)
                    print("order cancelled")
                    return  # Sai imediatamente após encontrar e remover a ordem
        print("order not found")

     
    # Função para modificar o preço ou quantidade das ordens   
    def modify_order(self, order_id, new_price=None, new_qty=None):
        modified_order = None
        
        # localiza e remove a ordem 
        for orders in [self.buy_orders, self.sell_orders, self.pegged_orders]:
            for order in orders: 
                if order.id == order_id:
                    modified_order = order
                    orders.remove(order)
                    break
                
        if modified_order:
            if new_price:
                modified_order.price = new_price
            if new_qty:
                modified_order.qty = new_qty
            print(f"order modified: {order_id}")
            
            if modified_order.side == "buy":
                self.buy_orders.append(modified_order)
            else:
                self.sell_orders.append(modified_order)
                
            self.sort_orders()
            self.update_pegged_orders()
        else: 
            print("order not found")
    #Funçao que ordena as ordens de compra em ordem decrescente de preço e as de venda em ordem crescente        
    def sort_orders(self):
        self.buy_orders = deque(sorted(self.buy_orders, key=lambda o: -o.price))
        self.sell_orders = deque(sorted(self.sell_orders, key=lambda o: o.price))
    
    # Função que atualiza o preço das ordens pegged     
    def update_pegged_orders(self): 
        best_bid = self.buy_orders[0].price if self.buy_orders else None
        best_offer = self.sell_orders[0].price if self.sell_orders else None
        
        for order in self.pegged_orders:
            if order.pegged_to == "bid" and best_bid is not None:
                order.price = best_bid
                if order not in self.buy_orders:
                    self.buy_orders.append(order)
            elif order.pegged_to == "offer" and best_offer is not None:
                order.price = best_offer
                if order not in self.sell_orders:
                    self.sell_orders.append(order)
                    
        self.sort_orders()
     # Exibe o book de ofertas   
    def print_book(self):
        print("\nOrdens de compra:")
        for order in self.buy_orders:
            print(f"{order.qty} @ {order.price}")
            
        print("\nOrdens de Venda:")
        for order in self.sell_orders:
            print(f"{order.qty} @ {order.price}")
            
def main():
    engine = MatchingEngine()
    print("Matching Engine inicializada")
    print("Insira uma ordem no formato: limit/market  buy/sell qty preço")
    print("Se for uma pegged o formato deverá ser:  peg bid/offer buy/sell qty")
    print("Para modificar a ordem: modify <id da ordem> <novo preço> <nova quantidade>")
    print("Para cancelar uma ordem: cancel <id da ordem>")
    print("Digite 'exit' para sair.")
    
    while True:
        user_input = input("Digite um comando:").strip().lower()
        if user_input == "exit":
            break
        try:
            parts = user_input.split()
            command = parts[0]
            
            if command == "peg":
                pegged_to = parts[1]
                side = parts[2]
                qty = int(parts[3])
                engine.add_order("limit", side, qty, pegged_to=pegged_to)
                
            elif command == "limit" or command == "market":
                side = parts[1]
                qty = int(parts[2])
                price = float(parts[3]) if len(parts) > 3 else None
                engine.add_order(command, side, qty, price)
                
            elif command == "modify":
                order_id = parts[1]
                new_price = float(parts[2])
                new_qty = int(parts[3]) if  len(parts) > 3 else None
                engine.modify_order(order_id, new_price, new_qty) 
            elif command == "cancel":
                order_id = parts[1]
                engine.cancel_order(order_id)
            else: 
                print("Comando desconhecido")
                
            engine.print_book()
            
        except (IndexError, ValueError) as e:
            print(f"Entrada invalida: {e}.")
    
main()       
    