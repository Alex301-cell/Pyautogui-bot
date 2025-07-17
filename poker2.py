import random
import itertools
from enum import Enum
from typing import List, Tuple, Dict, Optional
from collections import Counter

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    
    @property
    def display(self):
        displays = {
            2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
            11: "J", 12: "Q", 13: "K", 14: "A"
        }
        return displays[self.value]

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{self.rank.display}{self.suit.value}"
    
    def __repr__(self):
        return str(self)

class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        return self.cards.pop()

class PokerHand:
    def __init__(self, cards: List[Card]):
        self.cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
        self.rank, self.rank_values = self._evaluate_hand()
    
    def _evaluate_hand(self) -> Tuple[HandRank, List[int]]:
        ranks = [card.rank.value for card in self.cards]
        suits = [card.suit for card in self.cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = self._is_straight(ranks)
        
        # Royal Flush
        if is_flush and is_straight and min(ranks) == 10:
            return HandRank.ROYAL_FLUSH, [14]
        
        # Straight Flush
        if is_flush and is_straight:
            return HandRank.STRAIGHT_FLUSH, [max(ranks)]
        
        # Four of a Kind
        if 4 in rank_counts.values():
            quad = [rank for rank, count in rank_counts.items() if count == 4][0]
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.FOUR_OF_A_KIND, [quad, kicker]
        
        # Full House
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            trips = [rank for rank, count in rank_counts.items() if count == 3][0]
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            return HandRank.FULL_HOUSE, [trips, pair]
        
        # Flush
        if is_flush:
            return HandRank.FLUSH, sorted(ranks, reverse=True)
        
        # Straight
        if is_straight:
            return HandRank.STRAIGHT, [max(ranks)]
        
        # Three of a Kind
        if 3 in rank_counts.values():
            trips = [rank for rank, count in rank_counts.items() if count == 3][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.THREE_OF_A_KIND, [trips] + kickers
        
        # Two Pair
        if list(rank_counts.values()).count(2) == 2:
            pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], reverse=True)
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]
        
        # One Pair
        if 2 in rank_counts.values():
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.PAIR, [pair] + kickers
        
        # High Card
        return HandRank.HIGH_CARD, sorted(ranks, reverse=True)
    
    def _is_straight(self, ranks: List[int]) -> bool:
        sorted_ranks = sorted(set(ranks))
        if len(sorted_ranks) != 5:
            return False
        
        # Normal straight
        if sorted_ranks[-1] - sorted_ranks[0] == 4:
            return True
        
        # Wheel straight (A-2-3-4-5)
        if sorted_ranks == [2, 3, 4, 5, 14]:
            return True
        
        return False
    
    def __gt__(self, other):
        if self.rank.value != other.rank.value:
            return self.rank.value > other.rank.value
        return self.rank_values > other.rank_values

class Player:
    def __init__(self, name: str, chips: int = 1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
    
    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
    
    def bet(self, amount: int) -> int:
        actual_bet = min(amount, self.chips)
        self.chips -= actual_bet
        self.current_bet += actual_bet
        if self.chips == 0:
            self.all_in = True
        return actual_bet
    
    def fold(self):
        self.folded = True

class PokerBot(Player):
    def __init__(self, name: str, chips: int = 1000, aggression: float = 0.7, bluff_frequency: float = 0.15):
        super().__init__(name, chips)
        self.aggression = aggression
        self.bluff_frequency = bluff_frequency
    
    def calculate_hand_strength(self, community_cards: List[Card]) -> float:
        """Calculează forța mâinii curente"""
        all_cards = self.hand + community_cards
        if len(all_cards) < 5:
            return self._preflop_hand_strength()
        
        best_hand = self._get_best_hand(all_cards)
        return self._normalize_hand_strength(best_hand)
    
    def _preflop_hand_strength(self) -> float:
        """Evaluează forța mâinii preflop"""
        if len(self.hand) != 2:
            return 0.1
        
        card1, card2 = self.hand
        
        # Perechi
        if card1.rank.value == card2.rank.value:
            pair_strength = {
                14: 0.95,  # AA
                13: 0.90,  # KK
                12: 0.85,  # QQ
                11: 0.80,  # JJ
                10: 0.75,  # TT
                9: 0.70,   # 99
                8: 0.65,   # 88
                7: 0.60,   # 77
                6: 0.55,   # 66
                5: 0.50,   # 55
                4: 0.45,   # 44
                3: 0.40,   # 33
                2: 0.35    # 22
            }
            return pair_strength.get(card1.rank.value, 0.35)
        
        # Suited connectors și broadway cards
        high_card = max(card1.rank.value, card2.rank.value)
        low_card = min(card1.rank.value, card2.rank.value)
        suited = card1.suit == card2.suit
        
        base_strength = 0.1
        
        # Bonus pentru cărți înalte
        if high_card >= 11:  # J, Q, K, A
            base_strength += 0.3
        if low_card >= 11:
            base_strength += 0.2
        
        # Bonus pentru suited
        if suited:
            base_strength += 0.1
        
        # Bonus pentru connectors
        if abs(high_card - low_card) == 1:
            base_strength += 0.1
        
        return min(base_strength, 0.9)
    
    def _get_best_hand(self, cards: List[Card]) -> PokerHand:
        """Găsește cea mai bună mână de 5 cărți"""
        best_hand = None
        for combo in itertools.combinations(cards, 5):
            hand = PokerHand(list(combo))
            if best_hand is None or hand > best_hand:
                best_hand = hand
        return best_hand
    
    def _normalize_hand_strength(self, hand: PokerHand) -> float:
        """Normalizează forța mâinii la o valoare între 0 și 1"""
        strength_map = {
            HandRank.HIGH_CARD: 0.1,
            HandRank.PAIR: 0.25,
            HandRank.TWO_PAIR: 0.4,
            HandRank.THREE_OF_A_KIND: 0.55,
            HandRank.STRAIGHT: 0.7,
            HandRank.FLUSH: 0.8,
            HandRank.FULL_HOUSE: 0.9,
            HandRank.FOUR_OF_A_KIND: 0.95,
            HandRank.STRAIGHT_FLUSH: 0.98,
            HandRank.ROYAL_FLUSH: 1.0
        }
        return strength_map.get(hand.rank, 0.1)
    
    def calculate_pot_odds(self, pot_size: int, call_amount: int) -> float:
        """Calculează pot odds"""
        if call_amount == 0:
            return float('inf')
        return pot_size / call_amount
    
    def make_decision(self, pot_size: int, call_amount: int, community_cards: List[Card], 
                     min_raise: int) -> Tuple[str, int]:
        """Ia decizia botului"""
        if call_amount > self.chips:
            return "fold", 0
        
        hand_strength = self.calculate_hand_strength(community_cards)
        pot_odds = self.calculate_pot_odds(pot_size, call_amount)
        
        # Calculează probabilitatea de bluff
        should_bluff = random.random() < self.bluff_frequency
        
        # Logica de decizie
        if hand_strength >= 0.8 or (should_bluff and hand_strength >= 0.3):
            # Mână foarte bună sau bluff - raise agresiv
            if random.random() < self.aggression:
                raise_amount = min(min_raise + random.randint(50, 200), self.chips)
                return "raise", raise_amount
            else:
                return "call", call_amount
        
        elif hand_strength >= 0.6:
            # Mână bună - call sau raise moderat
            if random.random() < self.aggression * 0.7:
                raise_amount = min(min_raise + random.randint(25, 100), self.chips)
                return "raise", raise_amount
            else:
                return "call", call_amount
        
        elif hand_strength >= 0.4:
            # Mână mediocră - call dacă pot odds sunt bune
            if pot_odds >= 3 or call_amount <= 50:
                return "call", call_amount
            else:
                return "fold", 0
        
        elif hand_strength >= 0.2:
            # Mână slabă - call doar dacă este foarte ieftin
            if call_amount <= 25 or (pot_odds >= 5 and call_amount <= 50):
                return "call", call_amount
            else:
                return "fold", 0
        
        else:
            # Mână foarte slabă - fold
            return "fold", 0
    
    def get_decision_explanation(self, pot_size: int, call_amount: int, community_cards: List[Card], 
                               min_raise: int) -> str:
        """Returnează explicația deciziei botului"""
        hand_strength = self.calculate_hand_strength(community_cards)
        pot_odds = self.calculate_pot_odds(pot_size, call_amount)
        action, amount = self.make_decision(pot_size, call_amount, community_cards, min_raise)
        
        explanation = f"Forță mână: {hand_strength:.2f}, Pot odds: {pot_odds:.1f}"
        
        if action == "fold":
            explanation += " → FOLD (mână prea slabă)"
        elif action == "call":
            if call_amount == 0:
                explanation += " → CHECK"
            else:
                explanation += f" → CALL {call_amount}"
        elif action == "raise":
            explanation += f" → RAISE {amount}"
        
        return explanation

class AdvisorBot(PokerBot):
    """Bot special pentru a da sfaturi jucătorului"""
    def __init__(self, name: str, personality: str):
        super().__init__(name, 1000)
        self.personality = personality
        
        # Setează personalitatea
        if personality == "conservative":
            self.aggression = 0.4
            self.bluff_frequency = 0.05
        elif personality == "aggressive":
            self.aggression = 0.9
            self.bluff_frequency = 0.25
        elif personality == "balanced":
            self.aggression = 0.6
            self.bluff_frequency = 0.15
        elif personality == "tight":
            self.aggression = 0.3
            self.bluff_frequency = 0.02
        elif personality == "loose":
            self.aggression = 0.8
            self.bluff_frequency = 0.30

class PokerGame:
    def __init__(self):
        self.players = []
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_position = 0
        self.small_blind = 25
        self.big_blind = 50
        self.round_stage = "preflop"
        self.advisor_mode = False
        self.advisor_bots = []
        self.setup_advisors()
    
    def setup_advisors(self):
        """Setupează boții consilieri"""
        self.advisor_bots = [
            AdvisorBot("Conservative Carl", "conservative"),
            AdvisorBot("Aggressive Alice", "aggressive"),
            AdvisorBot("Balanced Bob", "balanced"),
            AdvisorBot("Tight Tommy", "tight"),
            AdvisorBot("Loose Lucy", "loose")
        ]
    
    def get_advisor_recommendations(self, player_hand: List[Card], pot_size: int, call_amount: int, min_raise: int) -> List[str]:
        """Obține recomandările de la toți boții consilieri"""
        recommendations = []
        
        for advisor in self.advisor_bots:
            # Setează mâna consilierului să fie aceeași cu a jucătorului
            advisor.hand = player_hand.copy()
            
            decision = advisor.get_decision_explanation(pot_size, call_amount, self.community_cards, min_raise)
            recommendations.append(f"{advisor.name}: {decision}")
        
        return recommendations
    
    def add_player(self, player: Player):
        self.players.append(player)
    
    def start_hand(self):
        """Începe o nouă mână"""
        # Reset pentru mâna nouă
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.round_stage = "preflop"
        
        # Reset jucători
        for player in self.players:
            player.reset_for_new_hand()
        
        # Elimină jucătorii fără chips
        self.players = [p for p in self.players if p.chips > 0]
        
        if len(self.players) < 2:
            print("Nu sunt suficienți jucători pentru a continua!")
            return False
        
        # Împarte cărțile
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.deal())
        
        # Blinds
        self._post_blinds()
        
        print("\n" + "="*50)
        print("MÂNĂ NOUĂ ÎNCEPE!")
        print("="*50)
        
        return True
    
    def _post_blinds(self):
        """Postează blinds"""
        if len(self.players) < 2:
            return
        
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (self.dealer_position + 2) % len(self.players)
        
        # Small blind
        sb_amount = self.players[sb_pos].bet(self.small_blind)
        self.pot += sb_amount
        print(f"{self.players[sb_pos].name} postează small blind: {sb_amount}")
        
        # Big blind
        bb_amount = self.players[bb_pos].bet(self.big_blind)
        self.pot += bb_amount
        self.current_bet = bb_amount
        print(f"{self.players[bb_pos].name} postează big blind: {bb_amount}")
    
    def betting_round(self):
        """Rundă de pariuri"""
        if self.round_stage == "preflop":
            first_to_act = (self.dealer_position + 3) % len(self.players)
        else:
            first_to_act = (self.dealer_position + 1) % len(self.players)
        
        active_players = [p for p in self.players if not p.folded and not p.all_in]
        if len(active_players) <= 1:
            return
        
        player_index = first_to_act
        players_acted = 0
        last_raiser = None
        
        while players_acted < len(active_players):
            player = self.players[player_index]
            
            if player.folded or player.all_in:
                player_index = (player_index + 1) % len(self.players)
                continue
            
            call_amount = max(0, self.current_bet - player.current_bet)
            min_raise = self.current_bet + self.big_blind
            
            if isinstance(player, PokerBot):
                action, amount = player.make_decision(self.pot, call_amount, 
                                                    self.community_cards, min_raise)
                
                if action == "fold":
                    player.fold()
                    print(f"{player.name} fold")
                elif action == "call":
                    if call_amount > 0:
                        bet_amount = player.bet(call_amount)
                        self.pot += bet_amount
                        print(f"{player.name} call {bet_amount}")
                    else:
                        print(f"{player.name} check")
                elif action == "raise":
                    total_bet = call_amount + amount
                    bet_amount = player.bet(total_bet)
                    self.pot += bet_amount
                    self.current_bet = player.current_bet
                    print(f"{player.name} raise la {player.current_bet}")
                    last_raiser = player_index
                    players_acted = 0  # Reset counter după raise
            else:
                # Jucător uman
                self._show_game_state(player)
                
                # Afișează recomandările consilierilor dacă este activat advisor mode
                if self.advisor_mode:
                    print("\n" + "="*50)
                    print("RECOMANDĂRI CONSILIERI:")
                    print("="*50)
                    recommendations = self.get_advisor_recommendations(player.hand, self.pot, call_amount, min_raise)
                    for rec in recommendations:
                        print(rec)
                    print("="*50)
                
                action, amount = self._get_human_action(player, call_amount, min_raise)
                
                if action == "fold":
                    player.fold()
                    print(f"{player.name} fold")
                elif action == "call":
                    if call_amount > 0:
                        bet_amount = player.bet(call_amount)
                        self.pot += bet_amount
                        print(f"{player.name} call {bet_amount}")
                    else:
                        print(f"{player.name} check")
                elif action == "raise":
                    total_bet = call_amount + amount
                    bet_amount = player.bet(total_bet)
                    self.pot += bet_amount
                    self.current_bet = player.current_bet
                    print(f"{player.name} raise la {player.current_bet}")
                    last_raiser = player_index
                    players_acted = 0  # Reset counter după raise
            
            players_acted += 1
            player_index = (player_index + 1) % len(self.players)
            
            # Verifică dacă toți jucătorii au acționat după ultimul raise
            if last_raiser is not None and player_index == last_raiser:
                break
        
        # Reset current_bet pentru următoarea rundă
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
    
    def _show_game_state(self, player: Player):
        """Afișează starea jocului pentru jucătorul uman"""
        print(f"\n--- {player.name} ({player.chips} chips) ---")
        print(f"Mâna ta: {' '.join(str(card) for card in player.hand)}")
        if self.community_cards:
            print(f"Community cards: {' '.join(str(card) for card in self.community_cards)}")
        print(f"Pot: {self.pot}")
        print(f"Current bet: {self.current_bet}")
        print(f"To call: {max(0, self.current_bet - player.current_bet)}")
    
    def _get_human_action(self, player: Player, call_amount: int, min_raise: int) -> Tuple[str, int]:
        """Obține acțiunea de la jucătorul uman"""
        while True:
            print("\nOpțiuni:")
            print("1. Fold")
            if call_amount > 0:
                print(f"2. Call {call_amount}")
            else:
                print("2. Check")
            print(f"3. Raise (minim {min_raise})")
            if self.advisor_mode:
                print("4. Arată din nou recomandările")
            
            try:
                choice = input("Alege opțiunea: ").strip()
                
                if choice == "1":
                    return "fold", 0
                elif choice == "2":
                    return "call", call_amount
                elif choice == "3":
                    while True:
                        try:
                            raise_amount = int(input(f"Introdu suma pentru raise (minim {min_raise}): "))
                            if raise_amount < min_raise:
                                print(f"Suma minimă pentru raise este {min_raise}")
                                continue
                            if raise_amount > player.chips:
                                print(f"Nu ai suficienți chips! Maxim: {player.chips}")
                                continue
                            return "raise", raise_amount
                        except ValueError:
                            print("Introdu un număr valid!")
                elif choice == "4" and self.advisor_mode:
                    print("\nRECOMANDĂRI CONSILIERI:")
                    recommendations = self.get_advisor_recommendations(player.hand, self.pot, call_amount, min_raise)
                    for rec in recommendations:
                        print(rec)
                    continue
                else:
                    print("Opțiune invalidă!")
            except KeyboardInterrupt:
                print("\nJocul a fost întrerupt!")
                return "fold", 0
    
    def deal_flop(self):
        """Împarte flop (3 cărți)"""
        self.deck.deal()  # Burn card
        for _ in range(3):
            self.community_cards.append(self.deck.deal())
        self.round_stage = "flop"
        print(f"\nFLOP: {' '.join(str(card) for card in self.community_cards)}")
    
    def deal_turn(self):
        """Împarte turn (1 carte)"""
        self.deck.deal()  # Burn card
        self.community_cards.append(self.deck.deal())
        self.round_stage = "turn"
        print(f"\nTURN: {' '.join(str(card) for card in self.community_cards)}")
    
    def deal_river(self):
        """Împarte river (1 carte)"""
        self.deck.deal()  # Burn card
        self.community_cards.append(self.deck.deal())
        self.round_stage = "river"
        print(f"\nRIVER: {' '.join(str(card) for card in self.community_cards)}")
    
    def determine_winner(self):
        """Determină câștigătorul"""
        active_players = [p for p in self.players if not p.folded]
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.pot
            print(f"\n{winner.name} câștigă {self.pot} chips prin fold!")
            return
        
        # Evaluează mâinile
        player_hands = []
        for player in active_players:
            all_cards = player.hand + self.community_cards
            best_hand = self._get_best_hand(all_cards)
            player_hands.append((player, best_hand))
        
        # Sortează după forța mâinii
        player_hands.sort(key=lambda x: x[1], reverse=True)
        
        # Determină câștigătorul
        winner, winning_hand = player_hands[0]
        winner.chips += self.pot
        
        print(f"\n--- REZULTAT ---")
        print(f"Community cards: {' '.join(str(card) for card in self.community_cards)}")
        for player, hand in player_hands:
            print(f"{player.name}: {' '.join(str(card) for card in player.hand)} "
                  f"({hand.rank.name}) - {player.chips} chips")
        
        print(f"\n{winner.name} câștigă {self.pot} chips cu {winning_hand.rank.name}!")
    
    def _get_best_hand(self, cards: List[Card]) -> PokerHand:
        """Găsește cea mai bună mână de 5 cărți"""
        best_hand = None
        for combo in itertools.combinations(cards, 5):
            hand = PokerHand(list(combo))
            if best_hand is None or hand > best_hand:
                best_hand = hand
        return best_hand
    
    def play_hand(self):
        """Joacă o mână completă"""
        if not self.start_hand():
            return False
        
        # Preflop
        print("\n--- PREFLOP ---")
        self.betting_round()
        
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) <= 1:
            self.determine_winner()
            return True
        
        # Flop
        self.deal_flop()
        self.betting_round()
        
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) <= 1:
            self.determine_winner()
            return True
        
        # Turn
        self.deal_turn()
        self.betting_round()
        
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) <= 1:
            self.determine_winner()
            return True
        
        # River
        self.deal_river()
        self.betting_round()
        
        # Showdown
        self.determine_winner()
        
        # Mută dealer button
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        
        return True
    
    def simulate_bot_vs_bot(self, num_hands: int = 10):
        """Simulează un joc doar între boți"""
        print("\n=== SIMULARE BOT VS BOT ===")
        
        # Creează doar boți
        bot_players = [
            PokerBot("Aggressive Annie", 1000, 0.8, 0.2),
            PokerBot("Conservative Carl", 1000, 0.4, 0.05),
            PokerBot("Balanced Bob", 1000, 0.6, 0.15),
            PokerBot("Tight Tommy", 1000, 0.3, 0.02),
            PokerBot("Loose Lucy", 1000, 0.9, 0.3)
        ]
        
        # Salvează jucătorii actuali
        original_players = self.players.copy()
        
        # Setează boții ca jucători
        self.players = bot_players
        
        # Joacă mai multe mâini
        for hand_num in range(1, num_hands + 1):
            print(f"\n{'='*50}")
            print(f"MÂNA {hand_num}")
            print(f"{'='*50}")
            
            if not self.play_hand():
                break
            
            # Afișează starea jucătorilor după fiecare mână
            print("\nSTARE JUCĂTORI:")
            for player in self.players:
                print(f"{player.name}: {player.chips} chips")
            
            # Elimină jucătorii care au rămas fără chips
            self.players = [p for p in self.players if p.chips > 0]
            
            if len(self.players) < 2:
                print("\nJocul s-a încheiat! Nu mai sunt suficienți jucători.")
                break
        
        # Determină câștigătorul final
        if len(self.players) > 0:
            winner = max(self.players, key=lambda p: p.chips)
            print(f"\n{'#'*50}")
            print(f"CÂȘTIGĂTOR FINAL: {winner.name} cu {winner.chips} chips!")
            print(f"{'#'*50}")
        
        # Restaurează jucătorii originali
        self.players = original_players
        
        return self.players
    
    def play_game(self):
        """Joacă un joc complet cu interacțiune umană"""
        print("=== POKER GAME ===")
        print("1. Joacă contra bot-uri")
        print("2. Simulează bot vs bot")
        print("3. Ieși")
        
        choice = input("Alege opțiunea: ").strip()
        
        if choice == "1":
            num_bots = int(input("Câți bot-uri vrei să joace? (1-5): "))
            if num_bots < 1 or num_bots > 5:
                print("Număr invalid! Folosesc 3 bot-uri.")
                num_bots = 3
            
            player_name = input("Introdu numele tău: ")
            self.add_player(Player(player_name))
            
            # Adaugă bot-uri
            bot_names = ["Aggressive Alice", "Balanced Bob", "Tight Tommy", "Loose Lucy", "Conservative Carl"]
            for i in range(num_bots):
                self.add_player(PokerBot(bot_names[i], 1000))
            
            # Activează advisor mode
            self.advisor_mode = input("Activezi advisor mode? (da/nu): ").lower() == "da"
            
            # Joacă mâini până când jucătorul uman iese sau rămâne fără chips
            while True:
                if not self.play_hand():
                    break
                
                # Verifică dacă jucătorul uman mai are chips
                human_players = [p for p in self.players if not isinstance(p, PokerBot)]
                if not human_players or human_players[0].chips <= 0:
                    print("\nAi rămas fără chips! Jocul s-a terminat.")
                    break
                
                # Verifică dacă vrea să continue
                cont = input("\nContinuăm? (da/nu): ").lower()
                if cont != "da":
                    break
        
        elif choice == "2":
            num_hands = int(input("Câte mâini să simulez? (1-100): "))
            if num_hands < 1 or num_hands > 100:
                print("Număr invalid! Folosesc 10 mâini.")
                num_hands = 10
            self.simulate_bot_vs_bot(num_hands)
        
        print("\nJoc încheiat!")

# Exemplu de utilizare
if __name__ == "__main__":
    game = PokerGame()
    game.play_game()