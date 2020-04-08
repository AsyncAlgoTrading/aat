#pragma once
#include <deque>
#include <string>
#include <pybind11/pybind11.h>

#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>

namespace py = pybind11;

namespace aat {
namespace core {

    class PriceLevel {
    public:
    private:
    };

    class Collector {
    public:
        void reset();

    private:
        py::function callback;
        std::deque<Event> event_queue;
        std::deque<Order> orders;
        std::deque<PriceLevel> price_levels;
    };

    class OrderBook {
    public:
        OrderBook(const std::string& name) {}

    private:
    };

} // namespace core
} // namespace aat
