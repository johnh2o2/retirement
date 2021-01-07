import numpy as np

def market_sim(avg_return, sharpe_ratio, seed=None):
    rand = np.random.RandomState(seed)
    return lambda _: avg_return * (1 + rand.randn() / sharpe_ratio)

def runway_sim(starting_amount, annual_expenses, market_return_func, max_runway = 100):
    balance = starting_amount
    years = 0
    while balance > 0 and years < max_runway:
        years += 1
        balance = (1 + market_return_func(years)) * (balance - annual_expenses)
    return years

def when_will_i_run_out_of_money_sim(current_age,
                                     retirement_age,
                                     current_savings,
                                     income,
                                     annual_expenses,
                                     market):
    age = current_age
    balance = current_savings
    while age < retirement_age:
        balance = (1 + market(age)) * (balance - annual_expenses + income)
        age += 1
    return age + runway_sim(balance, annual_expenses, market), balance

def get_retirement_age(current_age, current_savings, income, annual_expenses,
                       avg_return=0.05, sharpe_ratio=0.5, num_sims=1000, age_die=95, min_success_prob=0.5, seed=None):
    retirement_age = current_age
    market = market_sim(avg_return, sharpe_ratio, seed=seed)
    while True:
        ages_i_run_out_of_money, balances = zip(*[when_will_i_run_out_of_money_sim(current_age, retirement_age, current_savings,
                                                                             income, annual_expenses, market)
                                                  for _ in range(num_sims)])

        success_prob = sum(np.array(ages_i_run_out_of_money) >= age_die) / num_sims
        if success_prob > 0:
            print(f'retirement age: {retirement_age}; probability of retirement: {success_prob:0.5f}; average retirement savings: ${np.mean(balances):,.2f} +/- {np.std(balances):,.2f}')

        if success_prob > min_success_prob:
            return retirement_age

        retirement_age += 1


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='find out when you can retire!')
    parser.add_argument('--current-age', type=float, help="age you are....currently.", default=30)
    parser.add_argument('--current-savings', type=float, help='$aving$ in the bank', default=60000.)
    parser.add_argument('--avg-return', type=float, help='avg market return of portfolio', default=0.03)
    parser.add_argument('--sharpe-ratio', type=float, help='sharpe-ratio of portfolio', default=1.0)
    parser.add_argument('--num-sims', type=int, help='number of simulations to run', default=10000)
    parser.add_argument('--income', type=float, help='your income (before taxes)', default=206000.)
    parser.add_argument('--annual-expenses', type=float, help='how much does life cost you per year?', default=7000. * 12)
    parser.add_argument('--age-of-death', type=float, help='when do you plan on dying?', default=95.)
    parser.add_argument('--tax-rate', type=float, help='from 0 - 1 (default is 0.3)', default=0.35)
    parser.add_argument('--min-success-prob', type=float,
                        help='You can retire when the likelihood of NOT running out of money before you die is higher than this amount',
                        default=0.8)
    parser.add_argument('--seed', help="random seed", default=100)

    args = parser.parse_args()
    get_retirement_age(args.current_age,
                       args.current_savings,
                       (1 - args.tax_rate) * args.income,
                       args.annual_expenses,
                       avg_return=args.avg_return,
                       sharpe_ratio=args.sharpe_ratio,
                       num_sims=args.num_sims,
                       age_die=args.age_of_death, min_success_prob=args.min_success_prob)



