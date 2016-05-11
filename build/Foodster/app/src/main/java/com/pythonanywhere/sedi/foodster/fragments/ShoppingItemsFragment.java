package com.pythonanywhere.sedi.foodster.fragments;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.pythonanywhere.sedi.foodster.R;
import com.pythonanywhere.sedi.foodster.models.ShoppingList;

import java.util.List;

public class ShoppingItemsFragment extends Fragment {

    private ShoppingList sl;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_shopping_items, container, false);
        LinearLayout mainLayout = (LinearLayout) view.findViewById(R.id.items_layout);

        TextView description = (TextView) view.findViewById(R.id.descriptionView);
        description.setText(sl.getDescription());

        List<String> items = sl.getItems();
        for(int i=0; i<items.size(); i++) {
            TextView item = new TextView(getActivity());
            item.setText(items.get(i));

            mainLayout.addView(item);

        }

        return view;
    }

    public void setShoppingList(ShoppingList sl){
        this.sl = sl;
    }

}
